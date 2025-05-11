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

variable "allowed_email_domains" {
  description = "List of allowed email domains"
  type        = list(string)
  default     = ["example.com", "anotherdomain.com"]
}
