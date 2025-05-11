variable "name" {
  type = string
}

variable "region" {
  type = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
}

variable "allowed_email_domains" {
  description = "Comma-separated list of allowed Google email domains"
  type        = string
  default     = ""  # Empty means all domains are allowed
}
