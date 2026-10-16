from fastapi.testclient import TestClient

from app.config import Settings, validate_config_file
from app.main import app, reset_runtime_counters


client = TestClient(app)


def test_healthz() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_readyz() -> None:
    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"


def test_create_order() -> None:
    res = client.post("/orders", json={"sku": "SKU-1", "quantity": 2})
    assert res.status_code == 200
    body = res.json()
    assert body["sku"] == "SKU-1"
    assert body["quantity"] == 2
    assert body["status"] == "accepted"


def test_create_order_rejects_bad_quantity() -> None:
    res = client.post("/orders", json={"sku": "SKU-1", "quantity": 0})
    assert res.status_code == 422


def test_validate_good_dev_config(tmp_path) -> None:
    cfg = tmp_path / "dev.json"
    cfg.write_text('{"environment":"dev","database_url":"sqlite:///./demo.db"}', encoding="utf-8")
    settings = validate_config_file(str(cfg))
    assert isinstance(settings, Settings)
    assert settings.environment == "dev"


def test_validate_rejects_unknown_env(tmp_path) -> None:
    cfg = tmp_path / "bad.json"
    cfg.write_text('{"environment":"staging"}', encoding="utf-8")
    try:
        validate_config_file(str(cfg))
        assert False, "expected validation error"
    except Exception as exc:  # noqa: BLE001 — assert message content
        assert "environment" in str(exc).lower()


def test_metrics_expose_synthetic_error_rate(monkeypatch) -> None:
    monkeypatch.setenv("SYNTHETIC_ERROR_RATE", "0.05")
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    assert "checkout_synthetic_error_rate 0.05" in res.text
    assert "checkout_up 1" in res.text


def test_synthetic_error_rate_one_fails_orders(monkeypatch, caplog) -> None:
    monkeypatch.setenv("SYNTHETIC_ERROR_RATE", "1")
    reset_runtime_counters()
    with caplog.at_level("INFO", logger="checkout"):
        res = client.post("/orders", json={"sku": "SKU-1", "quantity": 1})
    assert res.status_code == 500
    assert "synthetic_failure" in caplog.text


def test_partial_synthetic_error_rate_is_deterministic(monkeypatch) -> None:
    monkeypatch.setenv("SYNTHETIC_ERROR_RATE", "0.2")
    reset_runtime_counters()
    codes = [
        client.post("/orders", json={"sku": "SKU-1", "quantity": 1}).status_code
        for _ in range(100)
    ]
    assert codes.count(500) == 20
    assert codes.count(200) == 80


def test_validate_rejects_sqlite_in_prod(tmp_path) -> None:
    cfg = tmp_path / "prod.json"
    cfg.write_text(
        '{"environment":"prod","database_url":"sqlite:///./demo.db"}',
        encoding="utf-8",
    )
    try:
        validate_config_file(str(cfg))
        assert False, "expected prod sqlite rejection"
    except ValueError as exc:
        assert "sqlite" in str(exc).lower()
