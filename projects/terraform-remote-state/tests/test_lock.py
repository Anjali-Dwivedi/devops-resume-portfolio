import threading

import pytest

from locksim import ConditionalCheckFailed, LockStore, contend


LOCK_ID = "EXAMPLE_STATE_BUCKET/env/dev/terraform.tfstate"


def test_second_acquire_loses_while_lock_is_held() -> None:
    store = LockStore()
    store.acquire(LOCK_ID, "team-a")
    with pytest.raises(ConditionalCheckFailed):
        store.acquire(LOCK_ID, "team-b")
    assert store.holder(LOCK_ID) == "team-a"


def test_wrong_owner_cannot_release() -> None:
    store = LockStore()
    store.acquire(LOCK_ID, "team-a")
    with pytest.raises(ConditionalCheckFailed):
        store.release(LOCK_ID, "team-b")
    assert store.holder(LOCK_ID) == "team-a"


def test_release_lets_the_other_team_acquire() -> None:
    store = LockStore()
    store.acquire(LOCK_ID, "team-a")
    store.release(LOCK_ID, "team-a")
    store.acquire(LOCK_ID, "team-b")
    assert store.holder(LOCK_ID) == "team-b"


def test_abandoned_lock_stays_until_force_unlock() -> None:
    store = LockStore()
    store.acquire(LOCK_ID, "team-a", operation="OperationTypeApply")
    # The owner exits without release. The record is still held.
    with pytest.raises(ConditionalCheckFailed):
        store.acquire(LOCK_ID, "team-b")
    with pytest.raises(ConditionalCheckFailed):
        store.release(LOCK_ID, "team-b")
    assert store.holder(LOCK_ID) == "team-a"
    removed = store.force_unlock(LOCK_ID)
    assert removed is not None
    assert removed.owner == "team-a"
    assert store.holder(LOCK_ID) is None
    store.acquire(LOCK_ID, "team-b")
    assert store.holder(LOCK_ID) == "team-b"


def test_concurrent_acquires_have_one_winner() -> None:
    store = LockStore()
    winners: list[str] = []
    errors: list[str] = []
    barrier = threading.Barrier(2)

    def attempt(owner: str) -> None:
        barrier.wait()
        try:
            store.acquire(LOCK_ID, owner)
            winners.append(owner)
        except ConditionalCheckFailed:
            errors.append(owner)

    threads = [threading.Thread(target=attempt, args=(name,)) for name in ("team-a", "team-b")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(winners) == 1
    assert len(errors) == 1
    assert store.holder(LOCK_ID) == winners[0]


def test_demo_transfers_lock_after_release() -> None:
    outcome = contend()
    assert outcome["team-a"] == "acquired"
    assert outcome["team-b"].startswith("blocked")
    assert outcome["after_release"] == "team-b"
