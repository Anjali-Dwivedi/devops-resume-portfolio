output "state_bucket_name" {
  description = "Bucket the remote backend example would use."
  value       = module.remote_state.bucket_name
}

output "lock_table_name" {
  description = "DynamoDB table the remote backend example would use."
  value       = module.remote_state.lock_table_name
}

output "terraform_ci_role_name" {
  description = "Least-privilege CI role name."
  value       = module.iam.terraform_ci_role_name
}

output "eks_enabled" {
  description = "EKS stub stays off unless a reviewed plan enables it."
  value       = module.eks.enabled
}

output "private_subnet_ids" {
  description = "Private subnets from the network module."
  value       = module.network.private_subnet_ids
}
