terraform {
  # Pins the DynamoDB-locking demonstration to the 1.9 line.
  # ~> 1.9.8 is >= 1.9.8 and < 1.10.0, so use_lockfile is not available here.
  # This is a portfolio compatibility pin, not an employer implementation date.
  required_version = "~> 1.9.8"

  required_providers {
    # Registry listing for 5.100.0 states Terraform 0.13+.
    # Exact pin keeps init reproducible. Provider 6.x is not used.
    aws = {
      source  = "hashicorp/aws"
      version = "5.100.0"
    }
  }

  # This root creates the remote backend. It must not store its own state there.
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region
  # Credentials come from the environment or a named profile.
  # Do not set access_key or secret_key in this configuration.
}
