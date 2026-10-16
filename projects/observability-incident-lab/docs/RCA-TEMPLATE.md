# RCA — <alert name>

## Summary

What fired, and whether this was synthetic or customer-facing.

## Detection

- Alert name and expression
- Stable `checkout_synthetic_error_rate`
- Canary `checkout_synthetic_error_rate`
- Canary weight at detection

## Triage

- Suspect track (stable or canary)
- `/readyz` on each track
- Whether logs contain `reason=synthetic_failure`
- Recent revision (`APP_VERSION`)

## Mitigation

- Controller action (`rollback`, `hold`, or `promote`)
- Weight and replica counts after the action
- Time the stable `/readyz` was healthy again

## Root cause

What changed. For this portfolio, say so if the cause was `SYNTHETIC_ERROR_RATE`.

## Prevention

Which test or config gate now covers the case. Do not claim an incident-rate reduction unless it was measured.
