import base64
import json
import requests
import os

import click

from google.cloud import storage
from google.oauth2.service_account import Credentials

import pubsub

API_BASE_URL = "https://datausa.io/api/data"


@click.command()
@click.option("-f", "--filename", required=True)
@click.option("-b", "--bucketname", required=True)
def main(bucketname, filename):
    sa_credentials = Credentials.from_service_account_info(
        json.loads(
            base64.b64decode(os.getenv("GCS_WRITER_CREDENTIALS"))
        )  # TODO: Rename if this works..
    )
    pubsub_publisher = pubsub.JobStatusChangePublisher(
        sa_credentials
    )  # SA Credentials seem not to be working... TODO: Test with direct scripts outside of container
    pubsub_publisher.publish_job_status_change(os.getenv("JOB_ID", ""), "processing")
    population_response = requests.get(f"{API_BASE_URL}?measures=Population")

    client = storage.Client(project=os.getenv("GCP_PROJECT_ID"), credentials=sa_credentials)
    bucket = client.get_bucket(bucketname)
    new_object_in_bucket = storage.Blob(filename, bucket)
    new_object_in_bucket.upload_from_string(json.dumps(population_response.json()))
    pubsub_publisher.publish_job_status_change(os.getenv("JOB_ID", ""), "finished")


if __name__ == "__main__":
    main()
