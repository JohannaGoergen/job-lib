resource "google_sql_database_instance" "instance" {
  region = var.gcp_region
  name = var.db_instance_name

  database_version = "POSTGRES_13"

  settings {
    tier = "db-f1-micro"
    backup_configuration {
      enabled = false
    }
  }

//  depends_on = [google_project_service.cloudsql_api]
}

resource "google_sql_database" "database" {
  name = var.database_name
  instance = google_sql_database_instance.instance.name

}

resource "google_sql_user" "user" {
  name = var.database_username
  instance = google_sql_database_instance.instance.name
  password = data.google_secret_manager_secret_version.db_password.secret_data
}
