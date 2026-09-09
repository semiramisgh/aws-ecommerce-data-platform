locals {
  raw_ingestion_lambda_name = "aws-ecommerce-raw-ingestion-monitor"
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "raw_ingestion_lambda" {
  name                 = "aws-ecommerce-raw-ingestion-monitor-role-sih3dfvf"
  path                 = "/service-role/"
  assume_role_policy   = data.aws_iam_policy_document.lambda_assume_role.json
  max_session_duration = 3600

  lifecycle {
    prevent_destroy = true
  }
}

data "aws_iam_policy_document" "lambda_basic_execution" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.raw_ingestion_lambda_name}:*",
    ]
  }
}

resource "aws_iam_policy" "lambda_basic_execution" {
  name   = "AWSLambdaBasicExecutionRole-0774fee8-144c-431a-8ad1-9d612d23059e"
  path   = "/service-role/"
  policy = data.aws_iam_policy_document.lambda_basic_execution.json

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "raw_ingestion_lambda" {
  role       = aws_iam_role.raw_ingestion_lambda.name
  policy_arn = aws_iam_policy.lambda_basic_execution.arn
}