#!/usr/bin/env bash
# Build single-stage vs multi-stage images and report sizes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Building multi-stage image"
docker build -t checkout-api:multi -f Dockerfile .

echo "==> Building single-stage image (comparison only)"
docker build -t checkout-api:single -f Dockerfile.singlestage .

multi_bytes="$(docker image inspect checkout-api:multi --format '{{.Size}}')"
single_bytes="$(docker image inspect checkout-api:single --format '{{.Size}}')"

python3 - <<PY
multi = int("${multi_bytes}")
single = int("${single_bytes}")
reduction = (1 - (multi / single)) * 100 if single else 0
print(f"single-stage: {single/1_000_000:.1f} MB")
print(f"multi-stage:  {multi/1_000_000:.1f} MB")
print(f"size reduction vs single-stage: {reduction:.1f}%")
print("NOTE: reduction is measured in this environment; do not treat as resume metric.")
PY
