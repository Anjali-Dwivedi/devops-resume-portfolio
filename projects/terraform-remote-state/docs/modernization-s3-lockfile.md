# Native S3 lock-file modernization

This document describes a later Terraform mechanism. The configurations in `bootstrap/` and `consumer/` do not enable it, and this repository has not migrated a backend to it.

## What changed

Terraform 1.10.0 (27 November 2024) added an experimental `use_lockfile` argument on the S3 backend. When it is true, Terraform writes a sibling object named `{key}.tflock`. If `dynamodb_table` is also set, Terraform acquires both locks and continues only when both succeed. The 1.10 upgrade guide says bucket and IAM policies may need permissions for that new object.

Terraform 1.11.0 (27 February 2025) made S3 native locking generally available and deprecated the DynamoDB backend arguments. The current S3 backend documentation still lists `dynamodb_table` as deprecated, not removed, and still defaults `use_lockfile` to false.

Terraform 1.9.8 does not have `use_lockfile`. The historical demonstration is pinned to `~> 1.9.8` so that argument cannot be set. DynamoDB locking is not unique to 1.9.8. It exists on earlier 1.x releases, and the current documentation still accepts the deprecated argument.

## Permissions are not the state-object permissions

The operator policy in `iam/backend-operator.json` grants `s3:GetObject` and `s3:PutObject` on the four state keys and does not grant `s3:DeleteObject`. That matches the Terraform 1.9.8 requirement for a default workspace: Terraform does not delete the state object.

A native lock file is a different object. Current S3 backend documentation requires `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` on `{key}.tflock` when `use_lockfile` is set. `DeleteObject` is how the lock object is removed. Granting it on the state key is a different, unnecessary permission. This demonstration does not add the `.tflock` permissions, because `use_lockfile` is not enabled.

## Migration

A later change, outside this demonstration, would:

1. Move clients to Terraform 1.10 or newer before setting `use_lockfile`.
2. Add `GetObject`, `PutObject`, and `DeleteObject` on each `{key}.tflock` object. Leave the state object without `DeleteObject` unless workspaces are introduced. Workspace state deletion is a separate Terraform 1.9 requirement and is not used here.
3. Optionally set both `use_lockfile` and `dynamodb_table` during the cutover. Both locks must be acquired. A missing permission on either side fails the operation.
4. Remove `dynamodb_table` only after every client is new enough to honor the S3 lock. Terraform 1.11 is the release that deprecated the DynamoDB arguments.

This repository stops at the documentation. No backend has been migrated.

## Rollback

Turning the native lock off, or destroying the lock object while a writer is alive, is the same class of hazard as `force-unlock`. Two writers can then update the same state object.

Removing the DynamoDB table before every client understands `use_lockfile` leaves older clients with no lock. Terraform 1.9.8 ignores an unknown `use_lockfile` argument only in the sense that this pin rejects 1.10 and later; an older binary simply does not implement the S3 lock.

Keeping both locks during rollback is safer than deleting either one first. Re-enabling `dynamodb_table` requires the table, the item permissions, and a Terraform version that still accepts the argument. The current documentation deprecates it and does not give a removal version.

## Sources

- Terraform 1.9.8 S3 backend: https://developer.hashicorp.com/terraform/language/v1.9.x/backend/s3
- Terraform 1.9.8 changelog, 16 October 2024: https://github.com/hashicorp/terraform/blob/v1.9.8/CHANGELOG.md
- Terraform 1.10.0 changelog and upgrade guide, S3 native locking: https://github.com/hashicorp/terraform/blob/v1.10.0/CHANGELOG.md and https://github.com/hashicorp/terraform/blob/v1.10.0/website/docs/language/upgrade-guides/index.mdx
- Terraform 1.11.0 changelog, DynamoDB arguments deprecated: https://github.com/hashicorp/terraform/blob/v1.11.0/CHANGELOG.md
- Current S3 backend page, `use_lockfile` and deprecated `dynamodb_table`: https://developer.hashicorp.com/terraform/language/backend/s3
