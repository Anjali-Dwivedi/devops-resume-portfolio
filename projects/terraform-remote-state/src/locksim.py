"""In-process simulation of a DynamoDB-style Terraform state lock.

Terraform 1.9.8 acquires the lock with PutItem and
ConditionExpression attribute_not_exists(LockID). The lock id is
bucket/key. This module copies that mutual-exclusion rule in memory so the
portfolio can show contention without calling AWS.

It does not perform a DynamoDB conditional write and it does not reproduce
Terraform's locking implementation. It is not an integration test.

Release here checks an owner string. Terraform 1.9.8 compares the lock-info
UUID and then calls DeleteItem with no condition. force_unlock below deletes
by the partition key. Terraform's force-unlock command requires that UUID.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass


class ConditionalCheckFailed(Exception):
    """Raised when a conditional write loses, matching DynamoDB's failure mode."""


@dataclass(frozen=True)
class LockInfo:
    lock_id: str
    owner: str
    operation: str
    created: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ID": self.lock_id,
            "Who": self.owner,
            "Operation": self.operation,
            "Created": self.created,
            "Path": self.lock_id,
        }


class LockStore:
    """Single-table lock store keyed by LockID."""

    def __init__(self) -> None:
        self._items: dict[str, LockInfo] = {}
        self._mu = threading.Lock()

    def acquire(self, lock_id: str, owner: str, operation: str = "OperationTypeApply") -> LockInfo:
        info = LockInfo(
            lock_id=lock_id,
            owner=owner,
            operation=operation,
            created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        with self._mu:
            if lock_id in self._items:
                holder = self._items[lock_id]
                raise ConditionalCheckFailed(
                    f"LockID {lock_id} held by {holder.owner} ({holder.operation})"
                )
            self._items[lock_id] = info
        return info

    def release(self, lock_id: str, owner: str) -> None:
        with self._mu:
            current = self._items.get(lock_id)
            if current is None or current.owner != owner:
                raise ConditionalCheckFailed(
                    f"LockID {lock_id} cannot be released by {owner}"
                )
            del self._items[lock_id]

    def holder(self, lock_id: str) -> str | None:
        with self._mu:
            current = self._items.get(lock_id)
            return None if current is None else current.owner

    def force_unlock(self, lock_id: str) -> LockInfo | None:
        """Delete the simulated item by partition key.

        This is not Terraform 1.9.8 force-unlock. That command passes the
        lock-info UUID into Unlock, which checks the UUID and then calls
        DeleteItem with no condition expression.
        """
        with self._mu:
            return self._items.pop(lock_id, None)


def contend(lock_id: str = "EXAMPLE_STATE_BUCKET/env/dev/terraform.tfstate") -> dict[str, str]:
    """Two teams apply at once. Exactly one acquire succeeds while the lock is held."""
    store = LockStore()
    results: dict[str, str] = {}

    def attempt(owner: str) -> None:
        try:
            store.acquire(lock_id, owner)
            results[owner] = "acquired"
        except ConditionalCheckFailed as exc:
            results[owner] = f"blocked: {exc}"

    first = threading.Thread(target=attempt, args=("team-a",))
    second = threading.Thread(target=attempt, args=("team-b",))
    # Serialize the first acquire so the demo outcome is stable, then race the second.
    first.start()
    first.join()
    second.start()
    second.join()

    holder = store.holder(lock_id)
    if holder != "team-a":
        raise RuntimeError(f"expected team-a to hold the lock, got {holder}")
    if not results["team-b"].startswith("blocked"):
        raise RuntimeError(f"expected team-b to be blocked, got {results['team-b']}")

    store.release(lock_id, "team-a")
    store.acquire(lock_id, "team-b")
    results["after_release"] = store.holder(lock_id) or "none"
    store.release(lock_id, "team-b")
    return results


def demo() -> int:
    outcome = contend()
    print("in-process lock simulation (not DynamoDB, no AWS API calls)")
    for key, value in outcome.items():
        print(f"  {key}: {value}")
    print("release transferred the lock; no cloud resources were created")
    return 0


if __name__ == "__main__":
    raise SystemExit(demo())
