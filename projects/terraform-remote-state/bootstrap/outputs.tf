output "state_bucket_name" {
  description = "Placeholder bucket name from configuration. No bucket has been created."
  value       = aws_s3_bucket.state.bucket
}

output "lock_table_name" {
  description = "Placeholder lock table name from configuration. No table has been created."
  value       = aws_dynamodb_table.lock.name
}

output "example_state_keys" {
  description = "Example object keys for separate roots that share this bucket. Not workspaces."
  value = [
    "env/dev/terraform.tfstate",
    "env/sit/terraform.tfstate",
    "env/uat/terraform.tfstate",
    "env/prod/terraform.tfstate",
  ]
}
