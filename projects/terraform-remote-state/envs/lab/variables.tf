variable "aws_region" {
  description = "Region used for provider configuration. Validate does not call AWS."
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Example bucket name. Not created by this lab."
  type        = string
  default     = "portfolio-tfstate-example"
}

variable "lock_table_name" {
  description = "Example lock table name. Not created by this lab."
  type        = string
  default     = "portfolio-tfstate-lock"
}

variable "github_repository" {
  description = "Repository allowed to assume the CI role after an approved apply."
  type        = string
  default     = "Anjali-Dwivedi/devops-resume-portfolio"
}

variable "allow_apply" {
  description = "Safety rail. Stays false so plan and apply fail. Variable validation also rejects true."
  type        = bool
  default     = false

  validation {
    condition     = var.allow_apply == false
    error_message = "Refusing to plan or apply. Cloud provisioning stays approval-gated."
  }
}

variable "github_oidc_provider_arn" {
  description = "Documentation placeholder ARN. Account 123456789012 is the AWS example account, not a live target."
  type        = string
  default     = "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
}
