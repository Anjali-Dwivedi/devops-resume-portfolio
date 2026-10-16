# CI/CD Container Platform

Independent reference implementation demonstrating GitHub Actions CI, Docker multi-stage builds, config validation quality gates, and multi-environment promotion patterns for a sample HTTP service.

**Resume mapping:** B03, B04, B05, B11, B12 (see `docs/portfolio/TRACEABILITY_MATRIX.md`).

## Problem

Teams need a repeatable path from commit → tested artifact → environment-specific deploy without manual snowflake steps. Failures should block promotion early (tests, image build, config validation).

## Architecture

<p align="center">
  <img src="../../docs/architecture/rendered/01-cicd-pipeline.svg" alt="CI/CD pipeline architecture" width="100%"/>
</p>

Also see: [multi-stage containers](../../docs/architecture/rendered/02-container-multistage.svg) · [network/data/control flows](../../docs/architecture/rendered/08-network-data-control-flows.svg) · [full gallery](../../docs/architecture/README.md)

## Why these tools

| Choice | Rationale | Rejected alternative |
|--------|-----------|----------------------|
| Python + FastAPI | Fast to test; clear health/readiness endpoints | Heavier Java stack for a demo service |
| Multi-stage Docker | Matches resume artifact standardization; measurable size win | Single-stage fat image |
| GitHub Actions | Aligns with stated CI tool; portable workflows | Jenkins-only (documented as optional enterprise pattern) |
| Compose profiles | Local multi-env without cloud cost | Immediate EKS (deferred; approval-gated) |

## Quick start

```bash
cd projects/ci-cd-container-platform
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload --port 8080
# health: curl -sf http://127.0.0.1:8080/healthz
```

### Docker

```bash
./scripts/build-and-compare.sh
docker compose --profile dev up --build
curl -sf http://127.0.0.1:8080/healthz
```

### Failure demos

```bash
# Config gate blocks bad env promotion
./scripts/demo-config-gate.sh

# Unit test failure path (optional intentional)
./scripts/demo-failing-test-gate.sh
```

## Verification checklist

- [ ] `pytest` passes
- [ ] Multi-stage image builds
- [ ] Size comparison script prints single-stage vs multi-stage
- [ ] Bad config fails validation (exit ≠ 0)
- [ ] Good config passes
- [ ] Compose `dev` profile serves `/healthz` and `/readyz`

## Security notes

- No real secrets in repo; `.env.example` only
- Image runs as non-root user
- CI should use OIDC to registries in real AWS accounts (not implemented here — no credentials)

## Limitations

- Deploy-to-cluster step is simulated locally; production EKS/ALB wiring lives in the progressive-delivery project
- Jenkins/Bitbucket parity is documented, not duplicated

## Interview discussion

See [`docs/INTERVIEW.md`](./docs/INTERVIEW.md).

## Cost

Local/CI only. No cloud resources required.
