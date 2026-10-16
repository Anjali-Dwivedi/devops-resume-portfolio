#!/usr/bin/env bash
# Schema-check static manifests and the rendered Helm chart.
# kubeconform uses published Kubernetes schemas and does not need a cluster.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v kubeconform >/dev/null 2>&1; then
  echo "kubeconform is required for offline manifest checks" >&2
  exit 1
fi

kubeconform -strict -summary -kubernetes-version 1.32.0 "$ROOT/deploy"

if ! command -v helm >/dev/null 2>&1; then
  echo "helm is not installed; static manifests passed kubeconform" >&2
  exit 0
fi

helm lint "$ROOT/chart/checkout"
rendered="$(mktemp --suffix=.yaml)"
helm template checkout "$ROOT/chart/checkout" --namespace checkout >"$rendered"
kubeconform -strict -summary -kubernetes-version 1.32.0 "$rendered"
rm -f "$rendered"
echo "manifest schema check passed"
