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
