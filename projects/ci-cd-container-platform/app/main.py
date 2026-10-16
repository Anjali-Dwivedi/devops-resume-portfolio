from __future__ import annotations

import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.config import Settings, load_settings

logger = logging.getLogger("checkout")

STARTED_AT = time.time()
_settings: Settings | None = None
_request_count = 0
_error_count = 0


def reset_runtime_counters() -> None:
    """Test helper. Production processes start at zero."""
    global _request_count, _error_count
    _request_count = 0
    _error_count = 0


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    get_settings()
    yield


app = FastAPI(title="checkout-api", version="1.0.0", lifespan=lifespan)


class OrderRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0, le=100)


class OrderResponse(BaseModel):
    order_id: str
    sku: str
    quantity: int
    status: str
    environment: str


def _synthetic_error_rate() -> float:
    raw = os.getenv("SYNTHETIC_ERROR_RATE", "0")
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _version() -> str:
    return os.getenv("APP_VERSION", "1.0.0")


def _fail_this_request(error_rate: float) -> bool:
    """Deterministic injector so demos do not depend on random draws.

    A rate of 0.2 fails 20 out of every 100 requests. A rate of 1 fails all.
    """
    global _request_count
    _request_count += 1
    if error_rate <= 0:
        return False
    if error_rate >= 1:
        return True
    percent = int(round(error_rate * 100))
    return (_request_count % 100) < percent


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, Any]:
    settings = get_settings()
    if not settings.ready:
        raise HTTPException(status_code=503, detail="not ready")
    return {
        "status": "ready",
        "environment": settings.environment,
        "version": _version(),
        "uptime_seconds": round(time.time() - STARTED_AT, 2),
    }


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    """Prometheus text exposition used by canary and incident demos."""
    settings = get_settings()
    error_rate = _synthetic_error_rate()
    uptime = time.time() - STARTED_AT
    observed = (_error_count / _request_count) if _request_count else 0.0
    version = _version().replace('"', "")
    environment = settings.environment.replace('"', "")
    lines = [
        "# HELP checkout_up 1 if the process is up",
        "# TYPE checkout_up gauge",
        "checkout_up 1",
        "# HELP checkout_uptime_seconds Process uptime in seconds",
        "# TYPE checkout_uptime_seconds gauge",
        f"checkout_uptime_seconds {uptime:.3f}",
        "# HELP checkout_synthetic_error_rate Configured synthetic error rate",
        "# TYPE checkout_synthetic_error_rate gauge",
        f"checkout_synthetic_error_rate {error_rate}",
        "# HELP checkout_requests_total Orders attempted",
        "# TYPE checkout_requests_total counter",
        f"checkout_requests_total {_request_count}",
        "# HELP checkout_request_errors_total Orders rejected by the synthetic injector",
        "# TYPE checkout_request_errors_total counter",
        f"checkout_request_errors_total {_error_count}",
        "# HELP checkout_observed_error_ratio errors divided by requests since start",
        "# TYPE checkout_observed_error_ratio gauge",
        f"checkout_observed_error_ratio {observed:.6f}",
        "# HELP checkout_build_info Build metadata for this process",
        "# TYPE checkout_build_info gauge",
        f'checkout_build_info{{version="{version}",environment="{environment}"}} 1',
    ]
    return "\n".join(lines) + "\n"


@app.post("/orders", response_model=OrderResponse)
def create_order(body: OrderRequest) -> OrderResponse:
    global _error_count
    settings = get_settings()
    error_rate = _synthetic_error_rate()
    if _fail_this_request(error_rate):
        _error_count += 1
        logger.info(
            json.dumps(
                {
                    "msg": "order_failed",
                    "reason": "synthetic_failure",
                    "error_rate": error_rate,
                    "environment": settings.environment,
                    "path": "/orders",
                }
            )
        )
        raise HTTPException(status_code=500, detail="synthetic failure injected")
    # Deterministic ID for demo reproducibility (not a security boundary).
    order_id = f"{settings.environment}-{body.sku}-{body.quantity}"
    return OrderResponse(
        order_id=order_id,
        sku=body.sku,
        quantity=body.quantity,
        status="accepted",
        environment=settings.environment,
    )
