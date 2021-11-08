resource "google_pubsub_topic" "job_status_updates_topic" {
  name = "job-status-updates"
  project = var.gcp_project_id
}

resource "google_pubsub_subscription" "push_job_status_updates" {
  name = "push-job-status-updates-to-ingester"
  topic = google_pubsub_topic.job_status_updates_topic.name

  ack_deadline_seconds = 20
  enable_message_ordering = true

  push_config {
    push_endpoint = "${google_cloud_run_service.job_api_service.status[0].url}/v1/job_status_updates"

    oidc_token {
      service_account_email = "${var.service_account_id}@${var.gcp_project_id}.iam.gserviceaccount.com"
      audience = var.oidc_token_audience
    }
    attributes = {
      x-goog-version = "v1"
    }

  }
}
