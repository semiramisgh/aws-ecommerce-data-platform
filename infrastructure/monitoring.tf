resource "aws_cloudwatch_log_group" "raw_ingestion_lambda" {
  name              = "/aws/lambda/${local.raw_ingestion_lambda_name}"
  retention_in_days = 7
  log_group_class   = "STANDARD"

  lifecycle {
    prevent_destroy = true
  }
}