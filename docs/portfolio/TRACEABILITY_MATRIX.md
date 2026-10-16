# Resume → Portfolio Traceability Matrix

Resume source (private, not in git): agent store `internal/resume/` + uploads PDF.  
Employer metrics are **historical claims**; portfolio evidence uses independently verified demos.

| ID | Resume theme | Portfolio project | Evidence | Type | Status |
|----|--------------|-------------------|----------|------|--------|
| B01 | Terraform remote state S3 + DynamoDB locking | `projects/terraform-remote-state` | Bootstrap, consumer, operator and break-glass recovery IAM, in-process lock simulation, Terraform 1.9.8 `validate`. Apply not run. Not employer code. | impl+test | verified local |
| B02 | Kubernetes adoption / standards for microservices | `projects/k8s-progressive-delivery` | Deployments, Services, Helm chart, kubeconform. Kind not started. | impl+test | verified local |
| B03 | CI/CD automation / pipeline optimisation | `projects/ci-cd-container-platform` | GitHub Actions workflow plus pytest | impl | verified tests |
| B04 | GitHub Actions: test, Docker build, deploy | `projects/ci-cd-container-platform` | `.github/workflows/ci-cd-container-platform.yml` and `portfolio.yml` | impl | workflow in repo |
| B05 | Docker multi-stage builds / smaller images | `projects/ci-cd-container-platform` | Dockerfile plus size script. Size numbers are from an earlier environment, not re-measured here. | impl | script present |
| B06 | Route53 + ALB + Ingress custom domains | `projects/k8s-progressive-delivery` | nginx Ingress in `deploy/`; ALB example is documentation only. No AWS load balancer. | impl+doc | local ingress only |
| B07 | Blue-green / canary + error-rate gate rollback | `projects/k8s-progressive-delivery` | `controller/canary.py` promote and rollback demos | impl+demo | verified local |
| B08 | Onboard teams to CI / remove manual steps | `docs/portfolio/ONBOARDING.md` | Onboarding steps and the portfolio workflow | doc | documented |
| B09 | RCA via logs/alerts | `projects/observability-incident-lab` | Synthetic incident, Prometheus rule, RCA. Not Splunk/Dynatrace/CloudWatch. | impl+demo | verified local |
| B10 | Faster triage / fewer recurring incidents | `projects/observability-incident-lab` | Runbook and rollback test. No incident-rate metric is claimed. | doc+demo | verified local |
| B11 | Multi-env deploys (dev/SIT/UAT/prod) | `projects/ci-cd-container-platform` | `configs/{dev,sit,uat,prod}.json` and compose profiles | impl | configs in repo |
| B12 | Catch env config issues pre-prod | `projects/ci-cd-container-platform` | `validate_config_file` rejects sqlite in prod. Covered by pytest. | demo | verified tests |
| B13 | Coordinated multi-env releases | `docs/portfolio/RELEASE-RUNBOOK.md` | Release order and rollback | doc | documented |
| B14 | Change mgmt / regulated compliance | `docs/portfolio/COMPLIANCE-NOTES.md` | Documentation-only. Not a certification and not an employer process. | doc-only | documented |

## Project grouping rationale

Four deep projects cover all technical bullets without shallow repo sprawl:

1. **ci-cd-container-platform** — B03, B04, B05, B11, B12 (+ supports B08)
2. **terraform-remote-state** — B01 (+ IAM/security themes)
3. **k8s-progressive-delivery** — B02, B06, B07
4. **observability-incident-lab** — B09, B10 (+ reliability narrative)

Landing repository indexes all four and links resume themes → demos.
