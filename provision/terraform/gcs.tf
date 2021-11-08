resource "google_storage_bucket" "sqlite_mount_bucket" {
  name = "gcp-job-lib-sqlite-mount"
  location = var.gcp_region
  project = var.gcp_project_id
}

resource "google_storage_bucket_iam_member" "default_sa_object_admin" {
  bucket = google_storage_bucket.sqlite_mount_bucket.name
  role = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.default_sa.email}"
}
