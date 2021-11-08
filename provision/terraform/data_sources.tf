data "google_secret_manager_secret_version" "secret_key" {
  secret = "DJANGO_SECRET_KEY"
  depends_on = [google_project_service.secrets_api]
}

data "google_secret_manager_secret_version" "gcs_writer_sa_credentials" {
  secret = "GCS_WRITER_CREDENTIALS"
  depends_on = [google_project_service.secrets_api]
}

data "google_secret_manager_secret_version" "db_password" {
  secret = "DATABASE_PASSWORD"
  depends_on = [google_project_service.secrets_api]
}
