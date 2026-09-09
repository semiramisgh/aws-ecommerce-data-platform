resource "aws_glue_workflow" "ecommerce_pipeline" {
  name                = "aws-ecommerce-data-pipeline"
  description         = "Orchestrates the raw-to-clean and clean-to-curated Glue jobs"
  max_concurrent_runs = 1
}

resource "aws_glue_trigger" "start_raw_to_clean" {
  name          = "aws-ecommerce-start-raw-to-clean"
  type          = "ON_DEMAND"
  workflow_name = aws_glue_workflow.ecommerce_pipeline.name

  actions {
    job_name = aws_glue_job.raw_to_clean.name
  }
}

resource "aws_glue_trigger" "start_clean_to_curated" {
  name              = "aws-ecommerce-start-clean-to-curated"
  type              = "CONDITIONAL"
  workflow_name     = aws_glue_workflow.ecommerce_pipeline.name
  start_on_creation = true

  predicate {
    logical = "AND"

    conditions {
      job_name         = aws_glue_job.raw_to_clean.name
      state            = "SUCCEEDED"
      logical_operator = "EQUALS"
    }
  }

  actions {
    job_name = aws_glue_job.clean_to_curated.name
  }
}
