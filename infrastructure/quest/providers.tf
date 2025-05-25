terraform {
  backend "s3" {
    region = "eu-central-1"
    bucket = "state-storage"
    key    = "quest"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.98"
    }
  }
}

provider "aws" {
  region = var.region
}
