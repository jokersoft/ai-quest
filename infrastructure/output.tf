output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "api_endpoint" {
  value = aws_api_gateway_stage.dev.invoke_url
}

output "rds_cluster_endpoint" {
  value = aws_rds_cluster.aurora_cluster.endpoint
}

output "rds_cluster_reader_endpoint" {
  value = aws_rds_cluster.aurora_cluster.reader_endpoint
}
