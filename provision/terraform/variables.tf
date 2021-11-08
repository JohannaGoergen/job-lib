variable "gcp_project_id" {
  type = string
}


variable "gcp_region" {
  type = string
  default = "europe-west3"  // Frankfurt
}

variable "cloudrun_service_name" {
  type = string
}

variable "app_image_tag"{
  type = string
  default = "latest"
}

variable "service_account_id" {
  type = string
}

variable "oidc_token_audience" {
  type = string
}

variable "app_location" {
  type = string
}

variable "gcp_project_number" {
  type = number
}

variable "allowed_hosts" {
  type = string
}

variable "database_username" {
  type =  string
}

variable "database_name" {
  type =  string
}

variable "db_instance_name" {
  type =  string
}

