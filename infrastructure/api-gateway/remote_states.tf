data "terraform_remote_state" "quest_api" {
  backend = "s3"

  config = {
    region = "eu-central-1"
    bucket = "state-storage"
    key    = "quest/api.json"
  }
}
