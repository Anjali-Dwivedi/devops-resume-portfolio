#!/usr/bin/env bash
# Local promote and rollback demos. No cluster and no cloud calls.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m controller.canary demo --mode promote
python3 -m controller.canary demo --mode rollback
echo "canary decision demos passed"
