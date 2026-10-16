# Tooling Remediation Plan

Install only when a project needs the tool. Prefer pinned versions documented in each project README.

## Priority installs (when unblocked)

1. **Docker Engine** (+ Compose) — local sample apps, CI-like builds
2. **Terraform** — IaC project
3. **kubectl + kind** (or k3d) — local Kubernetes demos without cloud cost
4. **helm** — if charts are justified by resume themes
5. **trivy** / **hadolint** / **shellcheck** — security and shell quality gates
6. Cloud CLIs — only after approved cloud plan and credentials available via env (never chat)

## Validation commands (to run after install)

```bash
docker version
docker compose version
terraform version
kubectl version --client
kind version
trivy --version
```
