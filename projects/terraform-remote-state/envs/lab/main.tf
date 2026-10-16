provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      project     = "devops-portfolio"
      managed_by  = "terraform"
      environment = "lab"
    }
  }
}

# Preconditions run at plan time, not during terraform validate.
# allow_apply defaults to false and variable validation rejects true,
# so neither plan nor apply can succeed.
resource "terraform_data" "cloud_apply_disabled" {
  input = "approval-gated"

  lifecycle {
    precondition {
      condition     = var.allow_apply
      error_message = "Cloud apply is disabled. This lab is validate-only until a human approves an AWS plan and removes this guard on purpose."
    }
  }
}

module "remote_state" {
  source = "../../modules/remote_state"

  state_bucket_name = var.state_bucket_name
  lock_table_name   = var.lock_table_name
}

module "network" {
  source = "../../modules/network"

  name               = "portfolio"
  vpc_cidr           = "10.40.0.0/16"
  enable_nat_gateway = false
}

module "iam" {
  source = "../../modules/iam"

  state_bucket_arn         = module.remote_state.bucket_arn
  lock_table_arn           = module.remote_state.lock_table_arn
  github_repository        = var.github_repository
  github_oidc_provider_arn = var.github_oidc_provider_arn
}

module "eks" {
  source = "../../modules/eks"

  enable_eks         = false
  cluster_name       = "portfolio"
  private_subnet_ids = module.network.private_subnet_ids
}
