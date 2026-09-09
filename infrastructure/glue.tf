resource "aws_glue_catalog_database" "clean" {
  name        = "ecommerce_clean"
  description = "Clean e-commerce datasets stored as Parquet in Amazon S3"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_glue_catalog_database" "curated" {
  name        = "ecommerce_curated"
  description = "curated e-commerce. analytics datasets stored as Parquet in Amazon S3"

  lifecycle {
    prevent_destroy = true
  }
}