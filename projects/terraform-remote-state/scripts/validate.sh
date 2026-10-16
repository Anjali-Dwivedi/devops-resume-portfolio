#!/usr/bin/env bash
# Validate Terraform and IAM policy rails. Does not plan or apply.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m src.iam_policy modules envs

if grep -R -n -E '^[[:space:]]*terraform apply' modules envs >/dev/null; then
  echo "cloud provisioning commands are not allowed under modules/ or envs/" >&2
  exit 1
fi

if ! command -v terraform >/dev/null 2>&1; then
  echo "terraform is not installed; IAM policy check passed and HCL validate was skipped" >&2
  exit 0
fi

terraform fmt -check -recursive "$ROOT"

(
  cd "$ROOT/envs/lab"
  terraform init -backend=false -input=false
  terraform validate
)

echo "terraform validate passed; no AWS resources were created"
