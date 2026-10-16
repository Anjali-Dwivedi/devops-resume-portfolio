# A second root that uses the remote backend.
# It intentionally creates no AWS resources. The backend configuration is the demonstration.

locals {
  example_state_keys = [
    "env/dev/terraform.tfstate",
    "env/sit/terraform.tfstate",
    "env/uat/terraform.tfstate",
    "env/prod/terraform.tfstate",
  ]

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
      error_message = "Refusing to plan or apply this consumer. This precondition is a demonstration guard, not a security boundary. terraform validate does not evaluate it. Backend initialization can run before it. Editing this file removes the guard."
    }
  }
}

output "example_state_keys" {
  description = "Pass one of these as key in a gitignored backend.hcl. Placeholders only."
  value       = local.example_state_keys
}
