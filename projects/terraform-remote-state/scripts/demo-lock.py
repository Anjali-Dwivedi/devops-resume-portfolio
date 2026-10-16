#!/usr/bin/env python3
"""Run the local state-lock simulation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from locksim import demo  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(demo())
