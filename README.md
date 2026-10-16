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
| [`projects/ci-cd-container-platform`](projects/ci-cd-container-platform) | GitHub Actions, Docker multi-stage, config gates, multi-env | Implementing |
| `projects/terraform-remote-state` | S3 + DynamoDB state locking, least-privilege IAM | Scaffolding |
| `projects/k8s-progressive-delivery` | Blue-green / canary, Ingress, error-rate rollback | Scaffolding |
| `projects/observability-incident-lab` | Metrics, synthetic failure, RCA runbooks | Scaffolding |

Traceability: [`docs/portfolio/TRACEABILITY_MATRIX.md`](docs/portfolio/TRACEABILITY_MATRIX.md)

---

## Operating rules

Autonomous agent instructions: [`AGENTS.md`](AGENTS.md) · Task tracker: [`docs/portfolio/TASK_TRACKER.md`](docs/portfolio/TASK_TRACKER.md)

### Publication note

Intended destination repo: [`Anjali-Dwivedi/devops-resume-portfolio`](https://github.com/Anjali-Dwivedi/devops-resume-portfolio).  
Current agent write access is on this repository (`Devops-`) until write permission is granted on the destination.
