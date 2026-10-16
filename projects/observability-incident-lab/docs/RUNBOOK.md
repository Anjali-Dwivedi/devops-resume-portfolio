# Runbook — checkout error-rate alert

Alert: `CheckoutCanaryErrorRateHigh`  
Rule: `checkout_synthetic_error_rate >= 0.05` for 1m  
Controller threshold: `0.05` in `projects/k8s-progressive-delivery/controller/canary.py`

## 1. Detect

Open the alert or run the local demo:

```bash
cd projects/observability-incident-lab
python3 scripts/demo-incident.py
```

Confirm the firing series is `checkout_synthetic_error_rate`, not a different metric with a similar name.

## 2. Triage

- Was a canary deployed? Ingress `checkout-canary` weight greater than 0 means yes.
- Scrape or curl `/metrics` on the stable pods and the canary pods. Compare the gauge.
- Curl `/readyz` on each. A 503 is a readiness failure, which is a different mitigation from a high error rate on a ready canary.
- Search logs for `"reason": "synthetic_failure"`. That field means the injector, not an upstream dependency, rejected the order.

## 3. Mitigate

| Suspect | Action |
|---------|--------|
| Canary at or above 0.05 | Roll back. Canary weight 0, canary replicas 0, stable replicas unchanged. |
| Stable unhealthy | Freeze promotion. Do not shift more traffic. Fix or roll the stable config. |
| Both under 0.05 | Do not mitigate. Keep evaluating until the sample minimum is met. |

```bash
cd ../k8s-progressive-delivery
python3 -m controller.canary demo --mode rollback
```

## 4. Learn

Copy `docs/RCA-TEMPLATE.md`, fill it from the commands above, and add a test if the failure was a new shape. The synthetic path already has `test_bad_canary_rolls_back_and_writes_rca`.

## What this runbook does not do

It does not page a human, open a cloud incident, or quote an improvement percentage. Those would be measurements from a real on-call rotation.
