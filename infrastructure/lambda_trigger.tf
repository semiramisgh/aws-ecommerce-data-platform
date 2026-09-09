resource "aws_lambda_permission" "allow_s3_raw_ingestion" {
  statement_id   = "lambda-fa61f57d-a336-41f6-b566-f8939f5e50ea"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.raw_ingestion_monitor.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = aws_s3_bucket.data_lake.arn
  source_account = data.aws_caller_identity.current.account_id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_notification" "raw_ingestion" {
  bucket = aws_s3_bucket.data_lake.id

  lambda_function {
    id                  = "db848429-cd65-4077-aec9-a131e417ee6d"
    lambda_function_arn = aws_lambda_function.raw_ingestion_monitor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/ecommerce"
    filter_suffix       = ".json"
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [
    aws_lambda_permission.allow_s3_raw_ingestion,
  ]
}