variable "name" {
  description = "Name prefix for IAM resources."
  type        = string
  default     = "portfolio"
}

variable "state_bucket_arn" {
  description = "ARN of the remote state bucket."
  type        = string
}

variable "lock_table_arn" {
  description = "ARN of the DynamoDB lock table."
  type        = string
}

variable "github_repository" {
  description = "GitHub repository allowed to assume the CI role, owner/name."
  type        = string
}

variable "github_oidc_provider_arn" {
  description = "ARN of the account's GitHub OIDC provider. Placeholder until an account is approved."
  type        = string
}

variable "tags" {
  description = "Extra tags."
  type        = map(string)
  default     = {}
}
