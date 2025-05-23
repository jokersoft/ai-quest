output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "api_endpoint" {
  value = aws_api_gateway_stage.dev.invoke_url
}

output "aws_security_group_id" {
  value = aws_security_group.lambda_sg.id
}
