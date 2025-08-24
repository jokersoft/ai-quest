resource "aws_dynamodb_table" "llm_token_usage" {
  name         = "${var.name}-llm-token-usage"
  billing_mode = "PAY_PER_REQUEST"  # On-demand pricing

  hash_key  = "service_date"
  range_key = "timestamp_request_id"

  attribute {
    name = "service_date"
    type = "S"
  }

  attribute {
    name = "timestamp_request_id"
    type = "S"
  }

  attribute {
    name = "model"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # Global Secondary Index for model queries
  global_secondary_index {
    name            = "model_index"
    hash_key        = "model"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # TTL configuration - auto-delete after 90 days
  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  # Encryption at rest
  server_side_encryption {
    enabled = true
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.name}-llm-token-usage"
    Environment = var.app_env
    Service     = "llm-tracking"
  }
}
