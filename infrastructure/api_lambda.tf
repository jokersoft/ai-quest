resource "aws_lambda_function" "api_lambda" {
  image_uri     = "${data.aws_ecr_repository.navan_lm.repository_url}:${var.image_version}"
  package_type  = "Image"
  function_name = "${var.name}-api-lambda"
  timeout       = 60
  role          = aws_iam_role.api_lambda.arn
  memory_size   = 1024

  environment {
    variables = {
      DEBUG = 1
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.api_lambda,
  ]
}
#
#resource "aws_lambda_function_url" "api_lambda" {
#  function_name      = aws_lambda_function.api_lambda.function_name
#  authorization_type = "NONE"
#
#  cors {
#    allow_credentials = true
#    allow_origins     = ["*"]
#    allow_methods     = ["*"]
#    allow_headers     = ["*"]
#    expose_headers    = ["*"]
#    max_age           = 86400
#  }
#}
