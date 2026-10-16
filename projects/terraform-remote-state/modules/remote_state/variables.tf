variable "state_bucket_name" {
  description = "Globally unique name for the Terraform state bucket."
  type        = string
}

variable "lock_table_name" {
  description = "DynamoDB table used as the Terraform state lock."
  type        = string
}

variable "tags" {
  description = "Extra tags applied to state resources."
  type        = map(string)
  default     = {}
}
