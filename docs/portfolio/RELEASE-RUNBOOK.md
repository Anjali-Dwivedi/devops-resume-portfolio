# Release runbook

Matches the environment promotion in the CI/CD diagram: dev, sit, uat, prod.

## Tracks

| Environment | Config | How it moves | Approval |
|-------------|--------|--------------|----------|
| dev | `projects/ci-cd-container-platform/configs/dev.json` | Local compose profile `dev`, or CI on a green main build | No |
| sit | `configs/sit.json` | Same gates as dev. Compose profile `sit` on port 8081 | No, once CI is green |
| uat | `configs/uat.json` | Compose profile `uat` on port 8082. Config must pass `validate_config.py` | Review the diff |
| prod | `configs/prod.json` | Canary project, not a direct apply | Required. Prod config cannot use sqlite |

## Order

1. Merge only when unit tests, the config gate, and the image build are green.
2. Run `scripts/demo-config-gate.sh` if the change touches config rules.
3. For a Kubernetes release, run `projects/k8s-progressive-delivery/scripts/demo-canary.sh` and read the decision log.
4. Shift canary weight only through `controller/canary.py` (10, then 50, then 100). Roll back if `checkout_synthetic_error_rate` is at or above `0.05`.
5. Stop if the Terraform lab is involved: that lab does not apply. An infrastructure change needs the approval recorded in `APPROVALS.md` first.

## Rollback

- Application: canary weight 0 and canary replicas 0. Stable stays.
- Config: revert the JSON and re-run the validator. Do not hot-edit prod to sqlite to "unblock" a demo.
- Infrastructure: nothing is applied in this repository, so there is no infra rollback to perform.

## What is not claimed

This runbook does not mean four cloud environments exist. dev/sit/uat are local config and compose profiles. Prod is the canary decision path plus the config gate.
