resource "aws_glue_crawler" "clean" {
  name          = "ecommerce-clean-crawler"
  description   = "Catalog clean Parquet datasets from Amazon S3"
  database_name = aws_glue_catalog_database.clean.name
  role          = "AWSGlueServiceRole-ecommerce-data-platform"

  configuration = jsonencode({
    Version              = 1.0
    CreatePartitionIndex = true
  })

  lineage_configuration {
    crawler_lineage_settings = "DISABLE"
  }

  recrawl_policy {
    recrawl_behavior = "CRAWL_EVERYTHING"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "DEPRECATE_IN_DATABASE"
  }

  s3_target {
    path       = "s3://aws-ecommerce-data-platform-sg-20260904/clean/"
    exclusions = []
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_glue_crawler" "curated" {
  name          = "ecommerce-curated-crawler"
  description   = "Catalog curated sales Parquet dataset from Amazon S3"
  database_name = aws_glue_catalog_database.curated.name
  role          = "AWSGlueServiceRole-ecommerce-data-platform"

  configuration = jsonencode({
    Version              = 1.0
    CreatePartitionIndex = true
  })

  lineage_configuration {
    crawler_lineage_settings = "DISABLE"
  }

  recrawl_policy {
    recrawl_behavior = "CRAWL_EVERYTHING"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "DEPRECATE_IN_DATABASE"
  }

  s3_target {
    path       = "s3://aws-ecommerce-data-platform-sg-20260904/curated/sales"
    exclusions = []
  }

  lifecycle {
    prevent_destroy = true
  }
}