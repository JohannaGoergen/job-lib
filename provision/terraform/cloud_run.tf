resource "google_cloud_run_service" "job_api_service" {
  name = var.cloudrun_service_name
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "europe-west3-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.jobs_api_images_registry.repository_id}/${var.cloudrun_service_name}"
        resources {
          limits = {
            memory = "256M"
          }
        }
        env {
          name = data.google_secret_manager_secret_version.secret_key.name
          value = data.google_secret_manager_secret_version.secret_key.secret_data
        }
        env {
          name = "GCP_PROJECT_ID"
          value = var.gcp_project_id
        }
        env {
          name = "GCP_REGION"
          value = var.gcp_region
        }
        env {
          name = data.google_secret_manager_secret_version.gcs_writer_sa_credentials.name
          value = data.google_secret_manager_secret_version.gcs_writer_sa_credentials.secret_data
        }
        env {
          name = "GCP_PROJECT_NUMBER"
          value = var.gcp_project_number
        }
        env {
          name = "OIDC_TOKEN_AUDIENCE"
          value = var.oidc_token_audience
        }
        env {
          name = "DATABASE_USERNAME"
          value = var.database_username
        }
        env {
          name = "DATABASE_NAME"
          value = var.database_name
        }
        env {
          name = "DATABASE_INSTANCE_NAME"
          value = var.db_instance_name
        }
        env {
          name = data.google_secret_manager_secret_version.db_password.name
          value = data.google_secret_manager_secret_version.db_password.secret_data
        }
        env {
          name = "ALLOWED_HOSTS"
          value = var.allowed_hosts
        }
      }
    }
  }
  traffic {
    percent = 100
    latest_revision = true
  }

  depends_on = [google_project_service.cloudrun_api]
}

data "google_iam_policy" "public_service" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers"
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_service.job_api_service.location
  project = google_cloud_run_service.job_api_service.project
  service = google_cloud_run_service.job_api_service.name

  policy_data = data.google_iam_policy.public_service.policy_data

  depends_on = [google_cloud_run_service.job_api_service]
}
