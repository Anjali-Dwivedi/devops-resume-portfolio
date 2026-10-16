output "bucket_name" {
  description = "State bucket name."
  value       = aws_s3_bucket.state.bucket
}

output "bucket_arn" {
  description = "State bucket ARN."
  value       = aws_s3_bucket.state.arn
}

output "lock_table_name" {
  description = "Lock table name."
  value       = aws_dynamodb_table.lock.name
}

output "lock_table_arn" {
  description = "Lock table ARN."
  value       = aws_dynamodb_table.lock.arn
}
