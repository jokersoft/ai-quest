data "terraform_remote_state" "app" {
  backend = "s3"

  config = {
    region = "eu-central-1"
    bucket = "state-storage"
    key    = "apps/ai-quest"
  }
}
