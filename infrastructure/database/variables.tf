variable "name" {
  type = string
}

variable "region" {
  type = string
}

variable "is_db_public" {
  description = "Boolean to determine if the database should be publicly accessible. Set to false for production environments."
  type        = bool
  default     = false
}
