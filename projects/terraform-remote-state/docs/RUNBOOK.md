# Runbook — Terraform remote state

## Validate

```bash
cd projects/terraform-remote-state
./scripts/validate.sh
```

Expected: IAM policy check prints `passed`, then `terraform validate` prints `Success`. No AWS API calls are required for validate.

## Show lock contention

```bash
python3 scripts/demo-lock.py
```

Expected: `team-a` acquires, `team-b` is blocked, and after release `team-b` acquires. This models the DynamoDB `LockID` conditional write. It is not a live table.

## What not to run

Do not run `terraform apply` in `envs/lab`. The plan-time guard is there so a plan fails before any resource is created. Do not delete that guard to "see if apply works" without an approved cloud plan.

## If validate fails

| Symptom | What to check |
|---------|----------------|
| Policy check lists an Allow wildcard | An `actions` value is `*`, `service:*`, or `iam:PassRole` without a `condition`. Deny statements are allowed to use `s3:*`. |
| `terraform init` cannot download the provider | Network access to `registry.terraform.io`. This is a provider download, not an apply. |
| `fmt -check` fails | Run `terraform fmt -recursive` from the project root and review the diff. |

## Rollback

There is nothing to roll back until an approved apply exists. After a future apply, state recovery is: S3 versioning on the state bucket, plus the lock table so a second apply cannot race the restore. That procedure stays documented until the bucket actually exists.
