# Anjali Dwivedi — DevOps Portfolio

Senior-interview DevOps / platform portfolio: **CI/CD**, **Kubernetes progressive delivery**, **Terraform remote state**, and **observability-driven incident response**.

> Independent reference implementations. Not employer source code. Resume metrics are historical; demo metrics are measured here.

---

## Architecture first

Interviewers should open the gallery before the code.

<p align="center">
  <img src="docs/architecture/rendered/hero-platform.svg" alt="Platform architecture hero diagram" width="100%"/>
</p>

**[Open the full Architecture Gallery →](docs/architecture/README.md)**

| Talk track | Diagram |
|------------|---------|
| System overview | [C4 containers](docs/architecture/rendered/10-c4-containers.svg) |
| Fail-closed delivery | [CI/CD gates](docs/architecture/rendered/01-cicd-pipeline.svg) |
| Zero-downtime releases | [Progressive delivery](docs/architecture/rendered/04-k8s-progressive-delivery.svg) · [Canary sequence](docs/architecture/rendered/05-canary-rollback-sequence.svg) |
| Concurrent IaC safety | [Terraform remote state](docs/architecture/rendered/03-terraform-remote-state.svg) |
| Incident readiness | [Failure recovery](docs/architecture/rendered/06-failure-recovery.svg) · [Observability](docs/architecture/rendered/07-observability-incident.svg) |
| Security boundaries | [IAM / secrets threat model](docs/architecture/rendered/09-iam-secrets-threat-model.svg) |

Editable sources: Mermaid (`.mmd`) + [flagship draw.io](docs/architecture/sources/flagship-platform.drawio).

---

## Projects

| Project | Resume themes | Status |
|---------|---------------|--------|
| [`projects/ci-cd-container-platform`](projects/ci-cd-container-platform) | GitHub Actions, Docker multi-stage, config gates, multi-env | Tests and gates in repo. Image-size demo needs Docker. |
| [`projects/terraform-remote-state`](projects/terraform-remote-state) | S3 + DynamoDB state locking, least-privilege IAM | Validate-only. No AWS apply. |
| [`projects/k8s-progressive-delivery`](projects/k8s-progressive-delivery) | Canary weight, Ingress, error-rate rollback | Controller and manifests verified without a cluster. |
| [`projects/observability-incident-lab`](projects/observability-incident-lab) | Metrics, synthetic failure, RCA | Decision path verified. Compose stack needs Docker. |

Traceability: [`docs/portfolio/TRACEABILITY_MATRIX.md`](docs/portfolio/TRACEABILITY_MATRIX.md)

---

## Operating rules

Autonomous agent instructions: [`AGENTS.md`](AGENTS.md) · Task tracker: [`docs/portfolio/TASK_TRACKER.md`](docs/portfolio/TASK_TRACKER.md)

### Cloud and publication

This repository is [Anjali-Dwivedi/devops-resume-portfolio](https://github.com/Anjali-Dwivedi/devops-resume-portfolio).

No AWS resources have been created. Terraform stays at `validate`. Kind and the Prometheus compose stack are local and were not started where Docker is absent. Publishing further or provisioning cloud resources still needs an explicit approval.
