output "function_name" {
  value = aws_lambda_function.api_lambda.function_name
}

output "invoke_arn" {
  value = aws_lambda_function.api_lambda.invoke_arn
}

output "aws_security_group_id" {
  value = aws_security_group.lambda_sg.id
}
