// Registry for images of the application itself
resource "google_artifact_registry_repository" "jobs_api_images_registry" {
  provider = google-beta

  repository_id = "jobs-api-images"
  project = var.gcp_project_id
  location = var.gcp_region
  format = "DOCKER"

  depends_on = [google_project_service.artifacts_registry_api]
}


// Registry for jobs to be run by the job runner service
resource "google_artifact_registry_repository" "registered_jobs_registry" {

  provider = google-beta

  repository_id = "registered-jobs-images"
  project = var.gcp_project_id
  location = var.gcp_region
  format = "DOCKER"

  depends_on = [google_project_service.artifacts_registry_api]
}
