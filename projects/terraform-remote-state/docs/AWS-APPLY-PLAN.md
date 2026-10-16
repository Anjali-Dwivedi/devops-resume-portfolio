# AWS apply plan — not executed

Status: **not approved and not run**. No bucket, table, VPC, role, or cluster was created. AWS CLI is not used by the lab scripts.

This document is the plan that would be reviewed before any apply. Costs below are published list-price order-of-magnitude figures for planning. They are not a bill and they are not a measurement. Re-check the AWS pricing page before approval.

## Inventory (only if later approved)

| Resource | Default in this repo | Why it exists |
|----------|----------------------|----------------|
| S3 bucket, versioning, SSE-S3, public access block, TLS deny policy | Described in `modules/remote_state` | Remote state |
| DynamoDB on-demand table, hash key `LockID`, PITR, SSE | Described in `modules/remote_state` | State lock |
| VPC, two public subnets, two private subnets, internet gateway | `modules/network` | Network module from the diagram |
| NAT gateway | **Off** (`enable_nat_gateway = false`) | About $0.045/hour plus data. Leave off. |
| IAM role for GitHub OIDC | `modules/iam` | Replaces long-lived keys |
| EKS control plane and node role | **Off** (`enable_eks = false`) | Control plane is about $0.10/hour. Leave off. |

Region in the example: `us-east-1`. Account: none. The placeholder ARN uses `123456789012`.

## Permissions the CI role would receive

- `s3:ListBucket` on the state bucket
- `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on `bucket/*`
- `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:DeleteItem` on the lock table

No `iam:*`, no `s3:*` on Allow, no `Resource: "*"`.

## Teardown, if an apply were ever approved

Destroy in reverse, from the same configuration, then confirm the bucket and table are gone. NAT and EKS must stay disabled so teardown cannot include them by surprise.

## Recurring cost if only state resources were created

S3 and on-demand DynamoDB for a small state file and a rarely written lock item are typically cents per month. That is still a charge, so it stays behind approval. NAT and EKS are deliberately excluded because they are not cents.

## This session

`terraform validate` and the local lock demo were run. A local `terraform plan -refresh=false` was run only to prove the guard. It failed on `var.allow_apply` is false and on missing AWS credentials. No state file was written. `terraform apply` was not run. The provider's credential lookup is not provisioning.
