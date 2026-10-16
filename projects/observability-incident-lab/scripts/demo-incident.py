#!/usr/bin/env python3
"""Run the synthetic incident path and print the RCA."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from incident.flow import Observation, investigate  # noqa: E402


def main() -> int:
    alert_text = (ROOT / "prometheus" / "alerts.yml").read_text(encoding="utf-8")
    observation = Observation(
        stable_error_rate=0.0,
        canary_error_rate=0.4,
        canary_weight=10,
        stable_ready=True,
        canary_ready=True,
    )
    result = investigate(observation, alert_text=alert_text)
    if not result.firing or result.decision_action != "rollback" or result.canary_weight != 0:
        print("incident demo did not roll the canary back", file=sys.stderr)
        return 1
    print(result.rca)
    print(
        f"incident demo passed: alert={result.alert_name} suspect={result.suspect} "
        f"action={result.decision_action}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
