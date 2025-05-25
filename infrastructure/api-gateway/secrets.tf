data "aws_secretsmanager_secret" "configs" {
  name = "ai-quest"
}

data "aws_secretsmanager_secret_version" "configs" {
  secret_id = data.aws_secretsmanager_secret.configs.id
}

locals {
  secrets = jsondecode(data.aws_secretsmanager_secret_version.configs.secret_string)
}
