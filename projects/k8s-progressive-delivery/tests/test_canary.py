from pathlib import Path

import pytest

from controller.canary import (
    DEFAULT_ERROR_THRESHOLD,
    Decision,
    RolloutState,
    Signal,
    decide,
    demo,
    ingress_canary_annotations,
    run_promotion,
)

ROOT = Path(__file__).resolve().parents[1]


def _state(weight: int = 10, stable: int = 2, canary: int = 1) -> RolloutState:
    return RolloutState("vN", "vN+1", weight, stable, canary)


def test_healthy_canary_steps_10_to_50_to_100() -> None:
    decisions = run_promotion(error_rate=0.0)
    assert [item.canary_weight for item in decisions] == [50, 100]
    assert decisions[-1].stable_replicas == 0
    assert decisions[-1].action == "promote"


def test_error_at_threshold_rolls_back() -> None:
    decision = decide(_state(10), Signal(DEFAULT_ERROR_THRESHOLD, 50))
    assert decision.action == "rollback"
    assert decision.canary_weight == 0
    assert decision.canary_replicas == 0
    assert decision.stable_replicas == 2


def test_error_above_threshold_on_first_step_stops() -> None:
    decisions = run_promotion(error_rate=0.4)
    assert len(decisions) == 1
    assert decisions[0].rolled_back


def test_just_under_threshold_promotes() -> None:
    decision = decide(_state(50), Signal(0.049, 50))
    assert decision.action == "promote"
    assert decision.canary_weight == 100
    assert decision.stable_replicas == 0


def test_insufficient_samples_hold() -> None:
    decision = decide(_state(10), Signal(0.9, 3))
    assert decision.action == "hold"
    assert decision.canary_weight == 10
    assert decision.canary_replicas == 1


def test_weight_zero_clears_canary_annotations() -> None:
    assert ingress_canary_annotations(0) == {}
    assert ingress_canary_annotations(10)["nginx.ingress.kubernetes.io/canary-weight"] == "10"


def test_weight_above_100_is_rejected() -> None:
    with pytest.raises(ValueError):
        ingress_canary_annotations(101)


def test_static_manifests_match_the_sequence() -> None:
    deploy = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "deploy").glob("*.yaml"))
    for kind in (
        "kind: Deployment",
        "kind: Service",
        "kind: Ingress",
        "kind: HorizontalPodAutoscaler",
        "kind: PodDisruptionBudget",
        "kind: NetworkPolicy",
        "kind: Role",
    ):
        assert kind in deploy
    assert 'nginx.ingress.kubernetes.io/canary-weight: "10"' in deploy
    assert "name: checkout-stable" in deploy
    assert "name: checkout-canary" in deploy
    assert "runAsNonRoot: true" in deploy
    assert "/readyz" in deploy
    assert "/healthz" in deploy


def test_chart_defaults_match_static_weight() -> None:
    values = (ROOT / "chart" / "checkout" / "values.yaml").read_text(encoding="utf-8")
    assert "weight: 10" in values
    template = (ROOT / "chart" / "checkout" / "templates" / "ingress.yaml").read_text(encoding="utf-8")
    assert "nginx.ingress.kubernetes.io/canary-weight" in template


def test_demo_commands() -> None:
    assert demo("promote") == 0
    assert demo("rollback") == 0


def test_decision_type() -> None:
    assert isinstance(decide(_state(), Signal(0, 20)), Decision)
