# State lock and recovery

Local checks do not need this runbook. It is the procedure for a disposable AWS account after an approved apply. Nothing in this repository has been applied.

State files contain resource ids and sometimes credentials. Do not print object bodies into logs, tickets, or this repository. Do not commit a `.tfstate` file.

## Lock held by someone else

Terraform reports the lock id, owner, operation, and creation time, then stops. The second operator does not write the state object.

Read the lock item. The partition key is `LockID`. For Terraform 1.9.8 the value is `{bucket}/{key}`, not the table name. Confirm the owner is still running before doing anything else.

Wait for that process. Do not delete the item because a plan is inconvenient.

## Process exited and left a lock

The DynamoDB item remains until it is deleted. A crash does not roll the S3 object back, and it does not prove the last `PutObject` finished.

1. Confirm the recorded process is gone. Check the host, CI job, and operation in the lock info.
2. If the process is alive, stop. `force-unlock` during an active write lets a second writer replace the object.
3. If it is dead, `terraform force-unlock LOCK_ID` removes the lock. `LOCK_ID` is the UUID in Terraform's lock error, not the DynamoDB partition key. Terraform 1.9.8 checks that UUID and then calls `DeleteItem` with no condition. This is break-glass. It does not restore state.
4. Read the state object and its versions before the next apply. Version reads use the separate policy below.

`src/locksim.py` is an in-process simulation. Its `force_unlock` deletes by partition key. It does not check a lock-info UUID and it does not call DynamoDB.

## Restore an older state version

Versioning on the bucket keeps prior copies of the object. Deleting the lock does not select one of those copies.

Practice on a disposable bucket first.

1. Stop other writers. Hold the lock for the restore, or confirm there is no live holder and take the lock after `force-unlock`.
2. With `iam/state-recovery.json` attached, list versions for one key, for example `env/dev/terraform.tfstate`. That policy allows `s3:ListBucketVersions` only when `s3:prefix` is one of the four example keys. Record `VersionId` and `LastModified` only.
3. `s3:GetObjectVersion` in that same policy reads the chosen version of those keys. Copy it to a path outside the repository and review it there. `iam/backend-operator.json` does not grant version reads.
4. Put the reviewed bytes back with the operator policy's `s3:PutObject` on that same key, or use `terraform state push` with the reviewed file, while the lock is held. The recovery policy does not grant `PutObject` or `DeleteObject`.
5. Release the lock.
6. Run a plan only when an AWS account is approved. This repository's local workflow does not run plan.

`s3:DeleteObject` is not granted on the state key. Recovery copies a version forward. It does not depend on deleting the current object. These permissions were not evaluated in IAM.

## Commands that touch AWS

These are not part of local validation and were not run here:

```bash
aws s3api list-object-versions --bucket "$BUCKET" --prefix "$KEY"
terraform force-unlock LOCK_ID
```

`list-object-versions` prints metadata. Do not follow it with a command that prints the object body into the terminal log.
