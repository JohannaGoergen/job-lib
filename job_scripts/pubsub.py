import json
import logging
import os

from typing import AnyStr

from google.cloud import pubsub

logger = logging.getLogger("PubSub")

MAX_RETRIES = 10


class JobStatusChangePublisher:
    def __init__(self, credentials):
        self.credentials = credentials

    @classmethod
    def _prepare_request_data(cls, job_id: AnyStr, status: str):
        data = json.dumps({"job_id": job_id, "status": status})
        return data.encode("utf-8")

    def publish_job_status_change(self, job_id: AnyStr, status: str, retries: int = 0):
        publisher = pubsub.PublisherClient(credentials=self.credentials)
        topic_path = publisher.topic_path(
            os.getenv("GCP_PROJECT_ID"), os.getenv("STATUS_CHANGE_PUBSUB_TOPIC")
        )
        future = publisher.publish(topic_path, data=self._prepare_request_data(job_id, status))
        future.add_done_callback(
            self._get_retry_callback(job_id, status, self.credentials, retries)
        )

    @classmethod
    def _get_retry_callback(cls, job_id: AnyStr, status: str, credentials, retries: int = 0):
        def callback(future):
            try:
                result = future.result()
                logger.info(
                    f"Publish result received:\n" f"| Result: {result}\n" f"| Retries: {retries}"
                )
            except Exception:
                if retries < MAX_RETRIES:
                    logger.warning(
                        f"Error while publishing:\n"
                        f"| Result: {future.exception()}\n"
                        f"| Retries: {retries}"
                    )
                cls(credentials).publish_job_status_change(job_id, status, retries + 1)

        return callback
