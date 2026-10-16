# Runbook — canary promote and rollback

## Healthy promotion

```bash
cd projects/k8s-progressive-delivery
python3 -m controller.canary demo --mode promote
```

Expected weights: 50, then 100. The last decision sets `stable_replicas` to 0.

## Bad canary

```bash
python3 -m controller.canary demo --mode rollback
```

Expected: one decision, action `rollback`, canary weight 0, canary replicas 0, stable replicas still 2.

## On a cluster

1. Confirm the canary Deployment is the one with `SYNTHETIC_ERROR_RATE` greater than 0. The stable Deployment should stay at `0`.
2. Read both `/metrics` endpoints and compare `checkout_synthetic_error_rate`.
3. If the canary is at or above `0.05`, set the canary Ingress weight to `0` (or delete that Ingress) and scale `checkout-canary` to 0.
4. Confirm `checkout-stable` still has ready pods and `/readyz` returns 200.
5. Write the incident note using the observability lab RCA template. Do not scale stable to 0 while investigating.

The controller's `decide` function is the source of those replica and weight numbers. Apply them with the deployer ServiceAccount, which can patch Deployments and Ingresses in `checkout` only.

## Manifest drift

`deploy/` is the kubectl bundle. `chart/checkout` is the Helm packaging of the same shape. Default canary weight is 10 in both. `tests/test_canary.py` checks that.
