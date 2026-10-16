# Portfolio Roadmap

## Canonical destination

- **Intended public portfolio repo:** https://github.com/Anjali-Dwivedi/devops-resume-portfolio  
- **Current agent write access:** only `Anjali-Dwivedi/Devops-` (push to `devops-resume-portfolio` returned 403 for `cursor[bot]`)  
- Until write access is granted, all work lands here and is marked for migration.

## Sequencing

| Priority | Project | Why first | Cloud cost |
|----------|---------|-----------|------------|
| P0 | `ci-cd-container-platform` | Foundation for every other demo; matches strongest CI/Docker bullets | None (local/CI) |
| P1 | `terraform-remote-state` | Core IaC bullet; validate/plan without applying | Local free; AWS optional (approval) |
| P2 | `k8s-progressive-delivery` | Blue-green/canary differentiator for senior interviews | kind local free; AWS EKS gated |
| P3 | `observability-incident-lab` | Release/reliability narrative (TA I experience) | Compose local free |

## Definition of “foundation complete”

- [x] Resume ingested (private)
- [x] Traceability matrix populated
- [ ] P0 project verified (tests + docker build + failure gate demo)
- [ ] P1 terraform validate passes
- [ ] P2 kind canary rollback demo scripted
- [ ] P3 synthetic incident demo scripted
- [ ] Landing README interview-ready
- [ ] Content migrated or pushed to `devops-resume-portfolio` (access gated)
