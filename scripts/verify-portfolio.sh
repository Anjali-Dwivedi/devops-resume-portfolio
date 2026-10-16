#!/usr/bin/env bash
# Local verification for the portfolio labs. Does not provision cloud resources.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== checkout-api =="
(
  cd "$ROOT/projects/ci-cd-container-platform"
  python3 -m pytest -q
)

echo "== terraform remote state =="
(
  cd "$ROOT/projects/terraform-remote-state"
  python3 -m pytest -q
  python3 scripts/demo-lock.py
  ./scripts/validate.sh
)

echo "== canary =="
(
  cd "$ROOT/projects/k8s-progressive-delivery"
  python3 -m pytest -q
  ./scripts/demo-canary.sh
  ./scripts/render-and-lint.sh
)

echo "== incident lab =="
(
  cd "$ROOT/projects/observability-incident-lab"
  python3 -m pytest -q
  python3 scripts/demo-incident.py >/tmp/portfolio-incident-rca.md
  test -s /tmp/portfolio-incident-rca.md
)

echo "portfolio verification passed; no cloud resources were created"
