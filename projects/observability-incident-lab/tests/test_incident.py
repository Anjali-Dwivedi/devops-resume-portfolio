import json
from pathlib import Path

from incident.flow import (
    Observation,
    alert_fires,
    investigate,
    load_canary,
    parse_synthetic_error_rate,
    threshold_from_alert_rule,
)

ROOT = Path(__file__).resolve().parents[1]
ALERTS = (ROOT / "prometheus" / "alerts.yml").read_text(encoding="utf-8")


def test_alert_threshold_matches_canary_controller() -> None:
    canary = load_canary()
    assert threshold_from_alert_rule(ALERTS) == canary.DEFAULT_ERROR_THRESHOLD == 0.05


def test_exact_threshold_fires_and_rolls_back() -> None:
    assert alert_fires(0.05, 0.05)
    result = investigate(
        Observation(0.0, 0.05, 10, True, True),
        alert_text=ALERTS,
    )
    assert result.firing
    assert result.suspect == "canary"
    assert result.decision_action == "rollback"
    assert result.canary_weight == 0


def test_healthy_canary_does_not_fire() -> None:
    result = investigate(
        Observation(0.0, 0.01, 10, True, True),
        alert_text=ALERTS,
    )
    assert result.firing is False
    assert result.decision_action == "hold"
    assert result.canary_weight == 10


def test_bad_canary_rolls_back_and_writes_rca() -> None:
    result = investigate(
        Observation(0.0, 0.4, 10, True, True),
        alert_text=ALERTS,
    )
    assert result.suspect == "canary"
    assert "automatic canary rollback" in result.mitigation
    assert "synthetic checkout error rate" in result.rca
    assert "SYNTHETIC_ERROR_RATE" in result.rca
    assert "not a customer incident" in result.rca


def test_stable_failure_freezes_promotion() -> None:
    result = investigate(
        Observation(0.2, 0.0, 10, False, True),
        alert_text=ALERTS,
    )
    assert result.suspect == "stable"
    assert result.decision_action == "hold"
    assert "config freeze" in result.mitigation


def test_metrics_parser_reads_gauge() -> None:
    text = "# TYPE checkout_synthetic_error_rate gauge\ncheckout_synthetic_error_rate 0.4\n"
    assert parse_synthetic_error_rate(text) == 0.4


def test_dashboard_and_compose_are_pinned() -> None:
    dashboard = json.loads((ROOT / "grafana" / "dashboards" / "checkout.json").read_text(encoding="utf-8"))
    assert dashboard["title"] == "Checkout incident lab"
    assert "checkout_synthetic_error_rate" in json.dumps(dashboard)
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "prom/prometheus:v3.15.0" in compose
    assert "prom/alertmanager:v0.34.1" in compose
    assert "grafana/grafana:13.2.4" in compose
    assert ":latest" not in compose
    assert "alerts.yml" in compose
