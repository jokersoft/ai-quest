output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "api_endpoint" {
  value = aws_api_gateway_deployment.lambda_api.invoke_url
}
