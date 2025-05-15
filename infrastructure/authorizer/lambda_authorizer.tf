# Lambda function for Google OAuth authorizer
resource "aws_lambda_function" "google_authorizer" {
  function_name = "${var.name}-google-authorizer"
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.authorizer_lambda.repository_url}:${var.image_tag}"
  role          = aws_iam_role.authorizer_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      GOOGLE_CLIENT_ID = local.secrets["google-client-id"]
      ALLOWED_DOMAINS  = join(",", var.allowed_email_domains)
    }
  }
}

# IAM role for the Lambda function
resource "aws_iam_role" "authorizer_role" {
  name = "${var.name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Basic execution policy for the authorizer Lambda
resource "aws_iam_role_policy_attachment" "authorizer_role" {
  role       = aws_iam_role.authorizer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Log group for the Lambda function
resource "aws_cloudwatch_log_group" "google_authorizer_log_group" {
  name              = "/aws/lambda/${var.name}-google-authorizer"
  retention_in_days = 1
}
