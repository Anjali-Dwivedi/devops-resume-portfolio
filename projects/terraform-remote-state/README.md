# Terraform Remote State Lab

Reference implementation of **S3 state + DynamoDB locking**, least-privilege IAM, and plan-before-apply rails.

**Resume mapping:** B01. Diagrams: [remote state](../../docs/architecture/rendered/03-terraform-remote-state.svg) · [IAM threat model](../../docs/architecture/rendered/09-iam-secrets-threat-model.svg)

<p align="center">
  <img src="../../docs/architecture/rendered/03-terraform-remote-state.svg" alt="Terraform remote state architecture" width="100%"/>
</p>

## Problem

Two engineers running `terraform apply` against the same state file will corrupt it unless a lock is acquired first. The state file also has to stay private, versioned, and encrypted. This lab shows that design and proves the lock rule locally. It does **not** create AWS resources.

## What is verified here

| Piece | Evidence |
|-------|----------|
| Conditional lock (one winner, owner-checked release) | `pytest` + `scripts/demo-lock.py` |
| No wildcard Allow IAM | `src/iam_policy.py` scans `modules/` and `envs/` |
| S3 versioning, SSE, public-access block, TLS deny, DynamoDB `LockID` | module `modules/remote_state` + unit assertions |
| `terraform validate` | `scripts/validate.sh` (`init -backend=false`, no plan, no apply) |
| Apply cannot succeed by accident | `allow_apply` defaults to false, variable validation rejects true, and the plan-time precondition checks that variable |

The lock script is a **local simulation** of DynamoDB's conditional `PutItem` / `DeleteItem`. It does not call AWS. The HCL is the real backend design, kept validate-only until a cloud plan is approved.

## Layout

| Path | Role |
|------|------|
| `modules/remote_state` | State bucket and lock table |
| `modules/network` | VPC and subnets. NAT defaults **off** (it is billable) |
| `modules/iam` | GitHub OIDC role that can touch only the state bucket and lock table |
| `modules/eks` | Optional cluster stub. `enable_eks` defaults **false** |
| `envs/lab` | Composition used for `terraform validate`, local backend |
| `envs/sandbox/backend.hcl.example` | Remote backend example. Not passed to `terraform init` |

## Run

```bash
cd projects/terraform-remote-state
python3 -m pytest -q
python3 scripts/demo-lock.py
./scripts/validate.sh
```

`validate.sh` needs Terraform 1.6 or newer. This repo was validated with **1.16.6** and the AWS provider **~> 6.69**.

## Safety rails

- `envs/lab` contains no `terraform apply`.
- A plan-time precondition fails closed so `terraform plan` and `terraform apply` error even if credentials are present.
- NAT and EKS are off. Turning them on is an approval decision; see [docs/AWS-APPLY-PLAN.md](docs/AWS-APPLY-PLAN.md).
- CI role trust is GitHub OIDC for `refs/heads/main` of this repository, not a long-lived access key.
- The account id `123456789012` in the lab variables is the AWS documentation example, not a target account.

## Interview notes

See [docs/INTERVIEW.md](docs/INTERVIEW.md) and [docs/RUNBOOK.md](docs/RUNBOOK.md).

## Cost

Local validation cost is zero. Nothing in this project has been applied, so there is no AWS bill from this lab.
