variable "aws_region" {
  description = "AWS region used by the project"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used for resource tags"
  type        = string
  default     = "aws-ecommerce-data-platform"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Name of the existing S3 data lake bucket"
  type        = string
  default     = "aws-ecommerce-data-platform-sg-20260904"
}