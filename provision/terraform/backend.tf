terraform {
  backend "gcs" {
    bucket = "gcp-job-lib-terraform"
    prefix = "terraform/state"

  }
}