"""Detect, triage, mitigate, and record a synthetic checkout incident.

The path matches docs/architecture/sources/07-observability-incident.mmd and
06-failure-recovery.mmd. Mitigation calls the canary controller so a bad
candidate is rolled back instead of promoted.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

THRESHOLD_EXPR = re.compile(
    r"expr:\s*checkout_synthetic_error_rate\s*>=\s*([0-9]*\.?[0-9]+)"
)
GAUGE_EXPR = re.compile(r"^checkout_synthetic_error_rate\s+([0-9]*\.?[0-9]+)\s*$", re.M)

LAB_ROOT = Path(__file__).resolve().parents[1]
CANARY_PATH = (
    LAB_ROOT.parent / "k8s-progressive-delivery" / "controller" / "canary.py"
)


def load_canary():
    root = str(CANARY_PATH.parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    from controller import canary as module

    return module


def threshold_from_alert_rule(text: str) -> float:
    match = THRESHOLD_EXPR.search(text)
    if match is None:
        raise ValueError("alert rule is missing checkout_synthetic_error_rate >= threshold")
    return float(match.group(1))


def alert_fires(error_rate: float, threshold: float) -> bool:
    return error_rate >= threshold


def parse_synthetic_error_rate(metrics_text: str) -> float:
    match = GAUGE_EXPR.search(metrics_text)
    if match is None:
        raise ValueError("metrics text has no checkout_synthetic_error_rate gauge")
    return float(match.group(1))


@dataclass(frozen=True)
class Observation:
    stable_error_rate: float
    canary_error_rate: float
    canary_weight: int
    stable_ready: bool
    canary_ready: bool


@dataclass(frozen=True)
class IncidentResult:
    alert_name: str
    firing: bool
    suspect: str
    mitigation: str
    decision_action: str
    canary_weight: int
    rca: str


def triage(observation: Observation) -> str:
    """Name the track that should be investigated first."""
    if observation.canary_weight > 0 and observation.canary_error_rate > observation.stable_error_rate:
        return "canary"
    if not observation.stable_ready or observation.stable_error_rate > 0:
        return "stable"
    if not observation.canary_ready:
        return "canary"
    return "none"


def mitigate(observation: Observation, threshold: float) -> tuple[str, str, int]:
    """Return mitigation label, controller action, and resulting canary weight."""
    canary = load_canary()
    suspect = triage(observation)
    if suspect == "canary" and alert_fires(observation.canary_error_rate, threshold):
        decision = canary.decide(
            canary.RolloutState("vN", "vN+1", observation.canary_weight, 2, 1),
            canary.Signal(observation.canary_error_rate, 50),
            threshold=threshold,
        )
        return (
            "automatic canary rollback; 100% of traffic stays on stable",
            decision.action,
            decision.canary_weight,
        )
    if suspect == "stable":
        return ("config freeze; no canary promotion while stable is unhealthy", "hold", observation.canary_weight)
    return ("no mitigation; signals are inside the promotion threshold", "hold", observation.canary_weight)


def render_rca(observation: Observation, result_bits: tuple[str, str, int], threshold: float) -> str:
    mitigation, action, weight = result_bits
    suspect = triage(observation)
    return "\n".join(
        [
            "# RCA — synthetic checkout error rate",
            "",
            "## Summary",
            "",
            "Alert `CheckoutCanaryErrorRateHigh` was evaluated against the local metrics fixture.",
            "This is a portfolio demo, not a customer incident and not a measured production SLO.",
            "",
            "## Detection",
            "",
            f"- Rule: `checkout_synthetic_error_rate >= {threshold}`.",
            f"- Stable error rate: {observation.stable_error_rate}.",
            f"- Canary error rate: {observation.canary_error_rate}.",
            f"- Canary ingress weight before mitigation: {observation.canary_weight}%.",
            "",
            "## Triage",
            "",
            f"- Suspect track: {suspect}.",
            f"- Stable `/readyz`: {'passing' if observation.stable_ready else 'failing'}.",
            f"- Canary `/readyz`: {'passing' if observation.canary_ready else 'failing'}.",
            "- Compare the two `checkout_synthetic_error_rate` series before blaming the database.",
            "- Structured logs use the field `reason=synthetic_failure` when the injector rejects an order.",
            "",
            "## Mitigation",
            "",
            f"- {mitigation}",
            f"- Controller action: `{action}`.",
            f"- Canary weight after mitigation: {weight}%.",
            "",
            "## Root cause",
            "",
            "The canary process was started with `SYNTHETIC_ERROR_RATE` high enough to cross the promotion threshold.",
            "No cloud resources were involved.",
            "",
            "## Prevention",
            "",
            "- Keep the canary controller threshold equal to the Prometheus rule.",
            "- The regression test `test_bad_canary_rolls_back_and_writes_rca` covers this path.",
            "- Do not promote when the sample count is below the controller minimum.",
            "",
        ]
    )


def investigate(
    observation: Observation,
    *,
    alert_text: str,
    alert_name: str = "CheckoutCanaryErrorRateHigh",
) -> IncidentResult:
    threshold = threshold_from_alert_rule(alert_text)
    firing = alert_fires(max(observation.stable_error_rate, observation.canary_error_rate), threshold)
    mitigation, action, weight = mitigate(observation, threshold)
    rca = render_rca(observation, (mitigation, action, weight), threshold)
    return IncidentResult(
        alert_name=alert_name,
        firing=firing,
        suspect=triage(observation),
        mitigation=mitigation,
        decision_action=action,
        canary_weight=weight,
        rca=rca,
    )
