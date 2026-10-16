# Resume → Portfolio Traceability Matrix

Resume source (private, not in git): agent store `internal/resume/` + uploads PDF.  
Employer metrics are **historical claims**; portfolio evidence uses independently verified demos.

| ID | Resume theme | Portfolio project | Evidence | Type | Status |
|----|--------------|-------------------|----------|------|--------|
| B01 | Terraform remote state S3 + DynamoDB locking | `projects/terraform-remote-state` | modules, local backend demo, optional AWS backend docs, `terraform validate` | impl+test | in progress |
| B02 | Kubernetes adoption / standards for microservices | `projects/k8s-progressive-delivery` + platform sample | Deployments, Services, Helm chart, kind demo | impl | pending |
| B03 | CI/CD automation / pipeline optimisation | `projects/ci-cd-container-platform` | GitHub Actions workflow, stage caching notes | impl+demo | in progress |
| B04 | GitHub Actions: test, Docker build, deploy | `projects/ci-cd-container-platform` | `.github/workflows/ci-cd-container-platform.yml` | impl | in progress |
| B05 | Docker multi-stage builds / smaller images | `projects/ci-cd-container-platform` | Dockerfile + size comparison script | impl+demo | in progress |
| B06 | Route53 + ALB + Ingress custom domains | `projects/k8s-progressive-delivery` | Ingress manifests + AWS design doc (cloud apply gated) | impl+doc | pending |
| B07 | Blue-green / canary + error-rate gate rollback | `projects/k8s-progressive-delivery` | Canary script, failure injection, rollback demo | impl+demo | pending |
| B08 | Onboard teams to CI / remove manual steps | Landing docs + platform README | Reusable workflow template + onboarding runbook | doc+impl | pending |
| B09 | RCA via logs/alerts (Splunk/Dynatrace/CW) | `projects/observability-incident-lab` | Synthetic incident + Prometheus/Grafana (CW patterns documented) | impl+demo | pending |
| B10 | Faster triage / fewer recurring incidents | `projects/observability-incident-lab` | Runbooks + preventive check demos | doc+demo | pending |
| B11 | Multi-env deploys (dev/SIT/UAT/prod) | `projects/ci-cd-container-platform` | env overlays / compose profiles | impl | pending |
| B12 | Catch env config issues pre-prod | `projects/ci-cd-container-platform` | Config validation gate that fails CI | demo | pending |
| B13 | Coordinated multi-env releases | Landing + release checklist | Release runbook | doc | pending |
| B14 | Change mgmt / regulated compliance | `docs/portfolio/COMPLIANCE-NOTES.md` | Documentation-only patterns (no employer process copy) | doc-only | pending |

## Project grouping rationale

Four deep projects cover all technical bullets without shallow repo sprawl:

1. **ci-cd-container-platform** — B03, B04, B05, B11, B12 (+ supports B08)
2. **terraform-remote-state** — B01 (+ IAM/security themes)
3. **k8s-progressive-delivery** — B02, B06, B07
4. **observability-incident-lab** — B09, B10 (+ reliability narrative)

Landing repository indexes all four and links resume themes → demos.
