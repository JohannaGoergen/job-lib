terraform {
  required_version = "~>1.0.10"

  required_providers {
    google = {
      version  = "4.0.0"
    }
    google-beta = {
      version  = "4.0.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
}

resource "google_project_service" "cloudrun_api" {
  service = "run.googleapis.com"
  disable_on_destroy = true
  depends_on = [google_project_service.service_api, google_project_service.resource_manager_api]
}

resource "google_project_service" "artifacts_registry_api" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = true
  depends_on = [google_project_service.service_api, google_project_service.resource_manager_api]
}

resource "google_project_service" "gcr_api" {
  service = "containerregistry.googleapis.com"
  disable_on_destroy = true
  depends_on = [google_project_service.service_api, google_project_service.resource_manager_api]
}

resource "google_project_service" "service_api" {
  service = "serviceusage.googleapis.com"
}

resource "google_project_service" "resource_manager_api" {
  service = "cloudresourcemanager.googleapis.com"
  depends_on = [google_project_service.service_api]
}

resource "google_project_service" "secrets_api" {
  service = "secretmanager.googleapis.com"

  disable_on_destroy = true

  depends_on = [google_project_service.service_api, google_project_service.resource_manager_api]
}

resource "google_project_service" "compute_api" {
  service = "compute.googleapis.com"

  disable_on_destroy = true

  depends_on = [google_project_service.service_api, google_project_service.resource_manager_api]
}

//resource "google_project_service" "cloudsql_api" {
//  service = "cloudsql.googleapis.com"
//
//  disable_on_destroy = true
//
//  depends_on = [google_project_service.service_api, google_project_service.resource_manager_api]
//}
