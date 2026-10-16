# Bootstrap creates only the remote-state backend: one S3 bucket and one DynamoDB lock table.
# It does not create a network, a cluster, or application infrastructure.

locals {
  # Terraform 1.9.8 rejects a precondition condition that is the bare literal false.
  # This local is that constant. It is not a variable and -var cannot change it.
  apply_allowed = false
}

resource "terraform_data" "apply_guard" {
  lifecycle {
    precondition {
      # A plan fails here. terraform validate does not evaluate this precondition.
      # Backend init can run before it. Editing this block removes the guard.
      # This is not a security boundary.
      condition     = local.apply_allowed
      error_message = "Refusing to plan or apply this bootstrap. This precondition is a demonstration guard, not a security boundary. terraform validate does not evaluate it. Backend initialization can run before it. Editing this file removes the guard."
    }
  }
}

resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "tls_only" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    actions = ["s3:*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    resources = [
      aws_s3_bucket.state.arn,
      "${aws_s3_bucket.state.arn}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "state" {
  bucket = aws_s3_bucket.state.id
  policy = data.aws_iam_policy_document.tls_only.json

  depends_on = [aws_s3_bucket_public_access_block.state]
}

resource "aws_dynamodb_table" "lock" {
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  # AWS-owned key. This block does not select a customer-managed KMS key.
  server_side_encryption {
    enabled = true
  }
}
