resource "aws_api_gateway_rest_api" "lambda_api" {
  name = "${var.name}-api"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "lambda_api" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id

  depends_on = [
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_method.proxy_method,
    aws_api_gateway_method.root_proxy_method,
    aws_api_gateway_authorizer.google_authorizer
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_method.proxy_method.id,
      aws_api_gateway_method.root_proxy_method.id,
      aws_api_gateway_method.health_method.id,
      aws_api_gateway_integration.lambda_integration.id,
      aws_api_gateway_integration.root_proxy_integration.id,
      aws_api_gateway_integration.health_integration.id,
      aws_api_gateway_authorizer.google_authorizer.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "dev" {
  deployment_id = aws_api_gateway_deployment.lambda_api.id
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  stage_name    = "dev"
}

# root proxy method
resource "aws_api_gateway_method" "root_proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "root_proxy_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_rest_api.lambda_api.root_resource_id
  http_method             = aws_api_gateway_method.root_proxy_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_lambda.invoke_arn
  content_handling        = "CONVERT_TO_TEXT"
}

# health
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "health_method" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "health_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.health_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_lambda.invoke_arn
}

# ANY (non-root)
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  # /{proxy+} doesn't match direct children of root like /health.
  # The proxy pattern only matches paths with at least one additional segment (like /path/subpath).
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id        = aws_api_gateway_rest_api.lambda_api.id
  resource_id        = aws_api_gateway_resource.proxy.id
  http_method        = "ANY"
  authorization      = "CUSTOM"
  authorizer_id      = aws_api_gateway_authorizer.google_authorizer.id
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_lambda.invoke_arn
  cache_key_parameters    = [
    "method.request.path.proxy",
  ]
  content_handling = "CONVERT_TO_TEXT"
}

# IAM
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}