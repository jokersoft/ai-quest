resource "aws_iam_policy" "api_lambda" {
  name        = "${var.name}-api-lambda"
  description = "${var.name}-api-lambda access"
  policy      = data.aws_iam_policy_document.api_lambda.json
}

data "aws_iam_policy_document" "api_lambda" {
  statement {
    actions   = [
      "autoscaling:Describe*",
      "cloudwatch:*",
      "logs:*",
      "secretsmanager:GetSecretValue",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses"
    ]
    resources = ["*"]
  }

  # Memory embedding
  statement {
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = [
      "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-embed-text-v2:0",
      "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-*",
      "arn:aws:bedrock:eu-central-1::foundation-model/*"
    ]
  }

  # Memory storage
  statement {
    actions = [
      "s3vectors:PutVectors",
      "s3vectors:GetVectors",
      "s3vectors:DeleteVectors",
      "s3vectors:QueryVectors",
      "s3vectors:GetIndex",
      "s3vectors:CreateIndex",
      "s3vectors:DeleteIndex",
      "s3vectors:ListIndexes"
    ]
    resources = ["*"]
  }

  # Token usage tracking
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:GetItem",
      "dynamodb:BatchWriteItem"
    ]
    resources = [
      aws_dynamodb_table.llm_token_usage.arn,
      "${aws_dynamodb_table.llm_token_usage.arn}/index/*"
    ]
  }
}

resource "aws_iam_role" "api_lambda" {
  name                  = "${var.name}-api-lambda"
  assume_role_policy    = data.aws_iam_policy_document.assume_role.json
  force_detach_policies = true
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "api_lambda" {
  role       = aws_iam_role.api_lambda.name
  policy_arn = aws_iam_policy.api_lambda.arn
}

resource "aws_lambda_permission" "url" {
  action        = "lambda:InvokeFunctionUrl"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "*"
  function_url_auth_type = "NONE"
}
