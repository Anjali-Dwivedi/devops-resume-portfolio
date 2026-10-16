# Portfolio Roadmap

## Canonical repository

https://github.com/Anjali-Dwivedi/devops-resume-portfolio

## Sequencing

| Priority | Project | Why first | Cloud cost |
|----------|---------|-----------|------------|
| P0 | `ci-cd-container-platform` | Foundation for every other demo | None (local/CI). Docker required for the image-size demo. |
| P1 | `terraform-remote-state` | State locking and IAM rails without apply | Local free. AWS apply still gated. |
| P2 | `k8s-progressive-delivery` | Canary weight and rollback | Decision demo is free. kind needs Docker. EKS gated. |
| P3 | `observability-incident-lab` | Detect, triage, mitigate, RCA | Python demo is free. Compose needs Docker. |

## Definition of foundation complete

- [x] Resume ingested (private, not in git)
- [x] Traceability matrix populated
- [x] P0 tests pass (image build not repeated in the 2026-10-16 environment)
- [x] P1 `terraform validate` passes and plan is refused
- [x] P2 canary rollback demo scripted and executed locally (kind cluster not started)
- [x] P3 synthetic incident demo scripted and executed
- [x] Landing README links the four projects and the gallery
- [x] Content is in `devops-resume-portfolio`
