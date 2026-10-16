# Kubernetes Progressive Delivery

Blue-green and canary rollouts with an **error-rate promotion gate** and automatic rollback.

**Resume mapping:** B02, B06, B07 · Diagrams: [progressive delivery](../../docs/architecture/rendered/04-k8s-progressive-delivery.svg) · [canary sequence](../../docs/architecture/rendered/05-canary-rollback-sequence.svg)

<p align="center">
  <img src="../../docs/architecture/rendered/04-k8s-progressive-delivery.svg" alt="Kubernetes progressive delivery" width="100%"/>
</p>

<p align="center">
  <img src="../../docs/architecture/rendered/05-canary-rollback-sequence.svg" alt="Canary rollback sequence" width="100%"/>
</p>

## Status

Scaffolding next: kind manifests, canary controller script using `checkout-api` `/metrics`, success + forced-failure demos.
