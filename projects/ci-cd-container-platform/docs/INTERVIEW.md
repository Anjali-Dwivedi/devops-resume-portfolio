# Interview Q&A — CI/CD Container Platform

Answers are grounded in **this** repository’s implementation.

## Q1: Why multi-stage builds instead of one stage?

**A:** The builder stage installs dependencies into a venv; the runtime stage copies only that venv plus application code, runs as UID 10001, and omits pip/build tooling. `scripts/build-and-compare.sh` measures the size delta in the current environment. Single-stage `Dockerfile.singlestage` exists only as a control for that demo—not for deployment.

## Q2: How do you prevent a bad config from reaching production?

**A:** `app.config.validate_config_file` enforces allowed environments (`dev|sit|uat|prod`) and rejects `sqlite` for `prod`. CI and `scripts/demo-config-gate.sh` run this as an explicit quality gate that exits non-zero on failure, blocking promotion before image deploy.

## Q3: What does `/readyz` buy you that `/healthz` does not?

**A:** `/healthz` is liveness (process up). `/readyz` checks application readiness via settings (`ready` flag / config load). Orchestrators can keep a pod out of Service endpoints until ready, which pairs with progressive delivery in the Kubernetes project.

## Q4: How would you wire this to real AWS deployments?

**A:** Build/push to ECR via OIDC; deploy with Helm/Argo or Actions + kubectl; gate prod with environment protection rules. This repo intentionally stops at verified local/CI evidence until a cloud plan is approved.

## Q5: What breaks if `SYNTHETIC_ERROR_RATE=1`?

**A:** `POST /orders` returns HTTP 500. That knob exists so the canary/error-rate project can force a rollback without changing application logic mid-demo.

## Challenging follow-ups to prepare for

- How would you cache pip layers without leaking secrets into the image?
- Where should DB credentials live if you replace the sample JSON `database_url`?
- How do you prove artifact integrity between CI and the cluster (signatures/SBOM)?
