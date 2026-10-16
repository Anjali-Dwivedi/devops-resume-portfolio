#!/usr/bin/env bash
# Local checks only: IAM policy scan, terraform fmt, init -backend=false, validate.
# Does not run terraform plan or terraform apply and does not call AWS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m src.iam_policy bootstrap consumer iam

if grep -R -n -E '^[[:space:]]*terraform (apply|plan)' bootstrap consumer iam >/dev/null; then
  echo "plan and apply commands are not allowed under bootstrap/, consumer/, or iam/" >&2
  exit 1
fi

if ! command -v terraform >/dev/null 2>&1; then
  echo "terraform 1.9.8 is not installed; static IAM check passed and HCL validate was skipped" >&2
  exit 1
fi

actual="$(terraform version -json | python3 -c 'import json,sys; print(json.load(sys.stdin)["terraform_version"])')"
if [[ "$actual" != "1.9.8" ]]; then
  echo "Terraform 1.9.8 is required for this demonstration, found ${actual}" >&2
  exit 1
fi

terraform fmt -check -recursive "$ROOT"

for config in bootstrap consumer; do
  (
    cd "$ROOT/$config"
    terraform init -backend=false -input=false
    terraform validate
  )
done

echo "terraform validate passed for bootstrap and consumer; no AWS resources were created"
