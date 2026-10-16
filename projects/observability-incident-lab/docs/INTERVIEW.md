# Interview Q&A — incident lab

## Why a gauge of the env var, not only the observed ratio?

`checkout_synthetic_error_rate` is deterministic: set it to `0.4` and the gate sees `0.4` without waiting for traffic. `checkout_observed_error_ratio` still exists so you can show that `POST /orders` really fails at that rate (20 failures per 100 requests at `0.2`, all requests at `1`). The alert and the canary controller both use the configured gauge so the demo and the rule cannot disagree.

## Why does mitigation import the canary controller?

The recovery diagram's mitigate step is the canary rollback, not a second copy of the threshold. `incident/flow.py` loads `controller/canary.py`. The test `test_alert_threshold_matches_canary_controller` fails if `alerts.yml` and `DEFAULT_ERROR_THRESHOLD` diverge.

## What is the difference between this and the resume's Splunk / Dynatrace / CloudWatch work?

The resume describes historical production tooling. This repository does not connect to those systems and does not repeat their numbers. Prometheus, Alertmanager, and Grafana are the local stand-in, and the verified part is the decision path, not a running Grafana screenshot, unless Docker was actually started.

## Why is Alertmanager a null receiver?

Paging someone from a portfolio demo would be noise. The RCA file is the record. A real receiver would be a later, approved integration. The rule, the labels, and the runbook URL are still real.

## What would you add for a second failure mode?

Stable `/readyz` failure already freezes promotion (`test_stable_failure_freezes_promotion`). A useful next case is a canary that is ready but only fails one route: keep the gate on that route's error ratio, and do not roll back on a single unsaturated sample. The controller's minimum sample count is the start of that answer.
