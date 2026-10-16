# Interview Q&A — Terraform remote state

Answers refer to this lab, not to an employer account.

## Why both S3 and DynamoDB?

S3 holds the state object (versioned, encrypted, private). DynamoDB holds the lock. Terraform's S3 backend writes `LockID` with a conditional put. Without the lock, two applies can overwrite each other's state. `src/locksim.py` demonstrates that rule: the second acquire fails until the owner releases it, and a different owner cannot delete the item.

## Why is `s3:*` present in the bucket policy?

It is on a **Deny** for `aws:SecureTransport = false`. A deny wildcard is how you block every S3 action over plain HTTP. The checker in `src/iam_policy.py` allows that and rejects the same wildcard on Allow. The CI policy names `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` only.

## What stops someone from applying this by habit?

`allow_apply` defaults to false. Variable validation rejects setting it to true, and a `terraform_data` precondition references that variable so `terraform plan` and `terraform apply` fail. `terraform validate` still passes, because preconditions run at plan time. NAT and EKS are separate booleans that default off, because those are the expensive resources.

## Why OIDC instead of access keys in GitHub secrets?

The threat model diagram calls out stolen long-lived keys. The IAM module's trust policy allows `sts:AssumeRoleWithWebIdentity` only for this repository's `main` branch. No static key is stored. The provider ARN in the lab is a placeholder, because no account has been attached.

## What would you change before a real apply?

Remove the plan-time guard only in a reviewed change, create the state backend first (it cannot store its own state on first create), commit the resulting `.terraform.lock.hcl`, and keep EKS and NAT off until a separate plan says otherwise. See `docs/AWS-APPLY-PLAN.md`.
