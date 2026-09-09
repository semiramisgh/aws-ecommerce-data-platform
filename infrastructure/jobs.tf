data "aws_caller_identity" "current" {}

locals {
  glue_common_default_arguments = {
    "--spark-event-logs-path" = "s3://aws-glue-assets-${data.aws_caller_identity.current.account_id}-${var.aws_region}/sparkHistoryLogs/"
    "--S3_BUCKET_NAME"        = var.s3_bucket_name
    "--enable-job-insights"   = "false"
    "--conf"                  = "spark.sql.catalog.glue_catalog.glue.skip-name-validation=true"
    "--job-bookmark-option"   = "job-bookmark-disable"
    "--job-language"          = "python"
    "--TempDir"               = "s3://${var.s3_bucket_name}/glue-temp/"
  }
}

resource "aws_glue_job" "raw_to_clean" {
  name              = "aws-ecommerce-raw-to-clean"
  role_arn          = aws_iam_role.glue_service.arn
  glue_version      = "6.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  max_retries       = 0
  timeout           = 10
  execution_class   = "STANDARD"

  default_arguments = merge(
    local.glue_common_default_arguments,
    {
      "--enable-continuous-cloudwatch-log" = "true"
    }
  )

  command {
    name            = "glueetl"
    script_location = "s3://${var.s3_bucket_name}/scripts/glue/glue-raw-to-clean.py"
    python_version  = "3"
  }

  execution_property {
    max_concurrent_runs = 1
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_glue_job" "clean_to_curated" {
  name              = "aws-ecommerce-clean-to-curated"
  description       = "Transforms clean Parquet datasets into curated"
  role_arn          = aws_iam_role.glue_service.arn
  glue_version      = "6.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  max_retries       = 0
  timeout           = 10
  execution_class   = "STANDARD"

  default_arguments = local.glue_common_default_arguments

  command {
    name            = "glueetl"
    script_location = "s3://${var.s3_bucket_name}/scripts/glue/aws-clean-to-curated.py"
    python_version  = "3"
  }

  execution_property {
    max_concurrent_runs = 1
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [name]
  }
}
