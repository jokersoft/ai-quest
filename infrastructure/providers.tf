terraform {
  backend "s3" {
    region = "eu-central-1"
    bucket = "state-storage"
    key    = "apps/ai-quest"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.10"
    }
  }
}

provider "aws" {
  region = var.region
}
