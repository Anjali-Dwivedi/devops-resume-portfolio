variable "aws_region" {
  description = "Placeholder region only. Not an employer region or account."
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Placeholder S3 bucket name. Not an employer bucket. This root is not applied."
  type        = string
  default     = "example-tfstate-bucket"

  validation {
    condition     = length(var.state_bucket_name) > 0
    error_message = "state_bucket_name must not be empty."
  }
}

variable "lock_table_name" {
  description = "Placeholder DynamoDB table name. Not an employer table. This root is not applied."
  type        = string
  default     = "example-tfstate-lock"

  validation {
    condition     = length(var.lock_table_name) > 0
    error_message = "lock_table_name must not be empty."
  }
}
