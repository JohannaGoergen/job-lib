resource "google_service_account" "default_sa" {
  account_id = var.service_account_id
  project = var.gcp_project_id
  description = "Default service account for backend infra"
  display_name = var.service_account_id
}
