# Partial backend. Values live in backend.hcl.example, not in this file.
# terraform init without -backend=false will try to reach AWS. The local workflow does not do that.
terraform {
  backend "s3" {}
}
