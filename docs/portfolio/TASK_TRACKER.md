# Portfolio Task Tracker

Last updated: 2026-10-16  
Repository: https://github.com/Anjali-Dwivedi/devops-resume-portfolio

## Phase 0 — Foundation

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P0-1 | Inspect workspace / tools | [x] | |
| P0-2 | AGENTS.md + Cursor rules | [x] | Includes diagram-priority rule |
| P0-3 | Trackers / checklist | [x] | |
| P0-4 | Ingest resume | [x] | Private copy; not in git |
| P0-5 | Land content in `devops-resume-portfolio` | [x] | `main` commit `6ec52f5` |

## Diagrams (priority)

| ID | Task | Status | Notes |
|----|------|--------|-------|
| D1 | Architecture gallery + hero SVG | [x] | `docs/architecture/` |
| D2 | 11 Mermaid sources rendered SVG/PNG | [x] | Re-rendered 2026-10-16 |
| D3 | Flagship draw.io board | [x] | `sources/flagship-platform.drawio` |
| D4 | README leads with diagrams | [x] | |
| D5 | Project READMEs embed diagrams | [x] | All four projects |
| D6 | Progressive-delivery diagram matches two Services | [x] | `04-k8s-progressive-delivery` |

## Implementation

| ID | Task | Status | Notes |
|----|------|--------|-------|
| I1 | Traceability matrix from resume | [x] | B01–B14 |
| I2 | ci-cd-container-platform | [x] | 10 pytest passed. Docker image compare not re-run here (no Docker). |
| I3 | terraform-remote-state | [x] | Bootstrap, consumer, and break-glass recovery policy. 27 pytest passed. `terraform validate` on 1.9.8 succeeded. Plan and apply were not run. |
| I4 | k8s-progressive-delivery | [x] | 11 pytest passed. Promote and rollback demos matched. kubeconform 13/13. Kind not started. |
| I5 | observability-incident-lab | [x] | 7 pytest passed. Incident demo rolled the canary back. Compose not started. |

## Verified 2026-10-16

The checkout-api, canary, and incident results below are from `./scripts/verify-portfolio.sh` on this revision.

- checkout-api: 10 passed
- Earlier remote-state lab: 11 pytest passed. `terraform validate` succeeded on Terraform 1.16.6 with AWS provider 6.69.1. `terraform plan -refresh=false` failed on `allow_apply = false` and on missing credentials. No state file was written. That lab configuration has been removed.
- This remote-state revision was checked with `python3 -m pytest -q` (`27 passed in 0.06s`) and `./scripts/validate.sh` on Terraform 1.9.8. Both roots were valid. Init reused `hashicorp/aws v5.100.0`. Validate does not evaluate the hardcoded precondition. A following `./scripts/verify-portfolio.sh` exited 0: remote-state pytest `27 passed in 0.03s`, checkout-api `10 passed`, canary `11 passed`, incident lab `7 passed`. Plan and apply were not run.
- canary tests: 11 passed. Promote weights 50 then 100. Rollback weight 0, canary replicas 0, stable replicas 2.
- kubeconform 1.32 schemas: 13 static resources valid, 13 rendered chart resources valid. Helm 4.3.1 lint passed.
- incident tests: 7 passed. Demo suspect `canary`, action `rollback`.

Earlier image-size measurement (previous environment, not repeated here): single-stage 439.5 MB → multi-stage 59.3 MB.

## Active blockers

1. Cloud apply remains approval-gated. The remote-state case study has no apply plan and creates no network or cluster.
2. Docker is not available in this environment, so kind and the Prometheus compose stack were not started.
