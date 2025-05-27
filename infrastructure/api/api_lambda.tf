resource "aws_lambda_function" "api_lambda" {
  image_uri     = "${data.aws_ecr_repository.api_lambda.repository_url}:${var.image_tag}"
  package_type  = "Image"
  function_name = "${var.name}-api-lambda"
  timeout       = 30
  role          = aws_iam_role.api_lambda.arn
  memory_size   = 256

  environment {
    variables = {
      # secrets
      DATABASE_URL = local.secrets["db-credentials"]
      API_KEY      = local.secrets["api-key"]
      ANTHROPIC_API_KEY = local.secrets["anthropic-api-key"]

      # configs
      IS_API_KEY_AUTH_DISABLED = 1  # Using gateway auth instead
      CONFIG_NAME             = "ai-quest"
      APP_VERSION             = var.image_tag
      DEBUG                   = 1
      HTTPX_LOG_LEVEL         = "WARNING"
      PYTHONDONTWRITEBYTECODE = 1
    }
  }

  # When you add vpc_config to a Lambda function, it loses default internet access - like Anthropic API.
  # vpc_config {
  #   subnet_ids = data.aws_subnets.default.ids
  #   security_group_ids = [aws_security_group.lambda_sg.id]
  # }

  depends_on = [
    aws_iam_role_policy_attachment.api_lambda,
  ]
}

resource "aws_security_group" "lambda_sg" {
  name        = "${var.name}-lambda-sg"
  description = "Security group for Lambda function"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# We can expose the Lambda function via an API Gateway or a Lambda Function URL.
# resource "aws_lambda_function_url" "api_lambda" {
#   function_name      = aws_lambda_function.api_lambda.function_name
#   authorization_type = "NONE"
#
#   cors {
#     allow_credentials = true
#     allow_origins = ["*"]
#     allow_methods = ["*"]
#     allow_headers = ["*"]
#     expose_headers = ["*"]
#     max_age           = 86400
#   }
# }

# Log group for the Lambda function
resource "aws_cloudwatch_log_group" "google_authorizer_log_group" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = 1
}
