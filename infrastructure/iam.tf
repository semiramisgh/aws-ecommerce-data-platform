data "aws_iam_policy_document" "glue_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue_service" {
  name                 = "AWSGlueServiceRole-ecommerce-data-platform"
  description          = "Allows Glue to call AWS services on your behalf. "
  assume_role_policy   = data.aws_iam_policy_document.glue_assume_role.json
  max_session_duration = 3600

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

data "aws_iam_policy_document" "glue_s3_access" {
  statement {
    sid    = "ListProjectBucket"
    effect = "Allow"

    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.data_lake.arn,
    ]
  }

  statement {
    sid    = "ReadProjectInputs"
    effect = "Allow"

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.data_lake.arn}/raw/ecommerce/*",
      "${aws_s3_bucket.data_lake.arn}/scripts/glue/*",
    ]
  }

  statement {
    sid    = "ManageProjectOutputs"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]

    resources = [
      "${aws_s3_bucket.data_lake.arn}/clean/*",
      "${aws_s3_bucket.data_lake.arn}/curated/*",
      "${aws_s3_bucket.data_lake.arn}/glue-temp/*",
    ]
  }
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name   = "EcommerceDataPlatformS3Access"
  role   = aws_iam_role.glue_service.name
  policy = data.aws_iam_policy_document.glue_s3_access.json
}