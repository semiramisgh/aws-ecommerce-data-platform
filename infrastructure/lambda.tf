data "archive_file" "raw_ingestion_monitor" {
  type        = "zip"
  output_path = "${path.module}/.terraform/raw_ingestion_monitor.zip"

  source {
    content  = file("${path.module}/../src/lambda/raw_ingestion_monitor.py")
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "raw_ingestion_monitor" {
  function_name = local.raw_ingestion_lambda_name
  description   = ""
  role          = aws_iam_role.raw_ingestion_lambda.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.14"

  filename         = data.archive_file.raw_ingestion_monitor.output_path
  source_code_hash = data.archive_file.raw_ingestion_monitor.output_base64sha256

  package_type  = "Zip"
  architectures = ["x86_64"]
  memory_size   = 128
  timeout       = 3

  environment {
    variables = {
      GLUE_WORKFLOW_NAME = aws_glue_workflow.ecommerce_pipeline.name
    }
  }

  ephemeral_storage {
    size = 512
  }

  tracing_config {
    mode = "PassThrough"
  }

  logging_config {
    log_format = "Text"
    log_group  = aws_cloudwatch_log_group.raw_ingestion_lambda.name
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.raw_ingestion_lambda,
    aws_iam_role_policy_attachment.lambda_start_glue_workflow
  ]
}
