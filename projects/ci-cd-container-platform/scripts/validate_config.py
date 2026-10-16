#!/usr/bin/env python3
"""CI quality gate: validate environment config files before promotion."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import validate_config_file  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to JSON config")
    args = parser.parse_args()
    try:
        settings = validate_config_file(str(args.config))
    except Exception as exc:  # noqa: BLE001 — gate must surface any failure
        print(f"CONFIG GATE FAILED: {exc}", file=sys.stderr)
        return 1
    print(
        f"CONFIG GATE PASSED: environment={settings.environment} "
        f"database_url={settings.database_url}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
