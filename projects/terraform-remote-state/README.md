# Terraform Remote State Lab

Reference implementation for **S3 + DynamoDB remote state locking**, module layout, and plan-before-apply safety rails.

**Resume mapping:** B01 · Diagram: [remote state](../../docs/architecture/rendered/03-terraform-remote-state.svg) · [IAM threat model](../../docs/architecture/rendered/09-iam-secrets-threat-model.svg)

<p align="center">
  <img src="../../docs/architecture/rendered/03-terraform-remote-state.svg" alt="Terraform remote state architecture" width="100%"/>
</p>

## Status

Scaffolding next: local backend demo (always free) + optional AWS backend module (apply gated on approval).

## Design intent

- Local backend for zero-cost `terraform validate` / `plan` demos
- Documented remote backend pattern matching resume theme without requiring live AWS until approved
- Explicit deny of wildcard IAM in example policies
