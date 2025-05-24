output "invoke_arn" {
  value = aws_lambda_function.google_authorizer.invoke_arn
}

output "arn" {
  value = aws_lambda_function.google_authorizer.arn
}

output "function_name" {
  value = aws_lambda_function.google_authorizer.function_name
}
