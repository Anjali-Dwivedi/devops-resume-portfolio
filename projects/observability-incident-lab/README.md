# Observability and Incident Lab

Synthetic failure, a Prometheus alert, and an RCA that ends in canary rollback.

**Resume mapping:** B09, B10. Diagrams: [observability](../../docs/architecture/rendered/07-observability-incident.svg) · [failure recovery](../../docs/architecture/rendered/06-failure-recovery.svg)

<p align="center">
  <img src="../../docs/architecture/rendered/07-observability-incident.svg" alt="Observability incident path" width="100%"/>
</p>

<p align="center">
  <img src="../../docs/architecture/rendered/06-failure-recovery.svg" alt="Failure and recovery" width="100%"/>
</p>

## Problem

When error rate moves, the on-call path should be the same every time: detect, compare stable with canary, mitigate, write the cause down. This lab uses `checkout-api`'s `SYNTHETIC_ERROR_RATE` so the failure is deliberate and reversible.

## What runs without Docker

`incident/flow.py` reads the same threshold as `prometheus/alerts.yml` (`checkout_synthetic_error_rate >= 0.05`) and calls the canary controller:

- canary above the threshold → automatic rollback, weight 0
- stable unhealthy → config freeze, no promotion
- both healthy → no mitigation

```bash
cd projects/observability-incident-lab
python3 -m pytest -q
python3 scripts/demo-incident.py
```

The demo prints an RCA. It says the case is synthetic. It does not claim a production page or a measured reduction in incidents.

## Compose stack, when Docker is available

Pinned images: Prometheus `v3.15.0`, Alertmanager `v0.34.1`, Grafana `13.2.4`.

```bash
# healthy
SYNTHETIC_ERROR_RATE=0 docker compose up --build

# incident
SYNTHETIC_ERROR_RATE=0.4 docker compose up --build
```

Grafana: http://localhost:3000 (local admin password defaults to `local-demo-only`; do not expose this port). Prometheus: http://localhost:9090. The verified run of this lab did not start the containers, because Docker was not available. The Python path is what was executed.

Alertmanager's receiver is `local-null`. The demo records the decision in the RCA instead of sending a page.

## Signals

| Signal | Where |
|--------|--------|
| `checkout_synthetic_error_rate` | Gauge from the `SYNTHETIC_ERROR_RATE` env var. This is what the gate uses. |
| `checkout_requests_total` / `checkout_request_errors_total` | Counters from `POST /orders` |
| JSON log `reason=synthetic_failure` | Application log line when the injector rejects an order |
| `/readyz` | Readiness, separate from the error-rate gate |

## Interview notes

[docs/INTERVIEW.md](docs/INTERVIEW.md) · [docs/RUNBOOK.md](docs/RUNBOOK.md) · [docs/RCA-TEMPLATE.md](docs/RCA-TEMPLATE.md)

## Cost

Local only. No CloudWatch, Splunk, or Dynatrace tenant is provisioned. Those tools appear on the resume as historical experience; this lab is the independent, verified path.
