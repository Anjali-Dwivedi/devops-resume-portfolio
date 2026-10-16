from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings, load_settings

STARTED_AT = time.time()
_settings: Settings | None = None


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
        "uptime_seconds": round(time.time() - STARTED_AT, 2),
    }


@app.get("/metrics")
def metrics() -> str:
    """Minimal Prometheus text exposition for progressive-delivery demos."""
    up = time.time() - STARTED_AT
    error_rate = float(os.getenv("SYNTHETIC_ERROR_RATE", "0"))
    lines = [
        "# HELP checkout_up 1 if process is up",
        "# TYPE checkout_up gauge",
        "checkout_up 1",
        "# HELP checkout_uptime_seconds Process uptime",
        "# TYPE checkout_uptime_seconds gauge",
        f"checkout_uptime_seconds {up:.3f}",
        "# HELP checkout_synthetic_error_rate Injected error rate for canary demos",
        "# TYPE checkout_synthetic_error_rate gauge",
        f"checkout_synthetic_error_rate {error_rate}",
    ]
    return "\n".join(lines) + "\n"


@app.post("/orders", response_model=OrderResponse)
def create_order(body: OrderRequest) -> OrderResponse:
    settings = get_settings()
    error_rate = float(os.getenv("SYNTHETIC_ERROR_RATE", "0"))
    if error_rate >= 1.0:
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
