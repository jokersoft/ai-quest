data "terraform_remote_state" "authorizer" {
  backend = "s3"

  config = {
    region = "eu-central-1"
    bucket = "state-storage"
    key    = "apps/ai-quest/authorizer"
  }
}

# API Gateway authorizer configuration
resource "aws_api_gateway_authorizer" "google_authorizer" {
  name                   = "google-authorizer"
  rest_api_id            = aws_api_gateway_rest_api.lambda_api.id
  authorizer_uri         = data.terraform_remote_state.authorizer.outputs.invoke_arn
  authorizer_credentials = aws_iam_role.api_gateway_authorizer_role.arn
  identity_source        = "method.request.header.Authorization"
  type                   = "TOKEN"
  # Cache the authorization result for 300 seconds (5 minutes)
  authorizer_result_ttl_in_seconds = 300
}

# IAM role for API Gateway to invoke the authorizer Lambda
resource "aws_iam_role" "api_gateway_authorizer_role" {
  name = "${var.name}-apigw-auth-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
}

# Policy to allow API Gateway to invoke the Lambda authorizer
resource "aws_iam_role_policy" "api_gateway_invoke_policy" {
  name = "${var.name}-apigw-invoke-policy"
  role = aws_iam_role.api_gateway_authorizer_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = data.terraform_remote_state.authorizer.outputs.arn
      }
    ]
  })
}

# Grant Authorizer Lambda permission to be invoked by API Gateway
resource "aws_lambda_permission" "api_gateway_authorizer" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = data.terraform_remote_state.authorizer.outputs.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/authorizers/${aws_api_gateway_authorizer.google_authorizer.id}"
}
