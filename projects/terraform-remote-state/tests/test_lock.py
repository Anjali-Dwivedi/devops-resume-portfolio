import threading

import pytest

from locksim import ConditionalCheckFailed, LockStore, contend


def test_second_acquire_loses_while_lock_is_held() -> None:
    store = LockStore()
    store.acquire("portfolio/lab/terraform.tfstate", "team-a")
    with pytest.raises(ConditionalCheckFailed):
        store.acquire("portfolio/lab/terraform.tfstate", "team-b")
    assert store.holder("portfolio/lab/terraform.tfstate") == "team-a"


def test_wrong_owner_cannot_release() -> None:
    store = LockStore()
    store.acquire("portfolio/lab/terraform.tfstate", "team-a")
    with pytest.raises(ConditionalCheckFailed):
        store.release("portfolio/lab/terraform.tfstate", "team-b")
    assert store.holder("portfolio/lab/terraform.tfstate") == "team-a"


def test_release_lets_the_other_team_acquire() -> None:
    store = LockStore()
    store.acquire("portfolio/lab/terraform.tfstate", "team-a")
    store.release("portfolio/lab/terraform.tfstate", "team-a")
    store.acquire("portfolio/lab/terraform.tfstate", "team-b")
    assert store.holder("portfolio/lab/terraform.tfstate") == "team-b"


def test_concurrent_acquires_have_one_winner() -> None:
    store = LockStore()
    winners: list[str] = []
    errors: list[str] = []
    barrier = threading.Barrier(2)

    def attempt(owner: str) -> None:
        barrier.wait()
        try:
            store.acquire("portfolio/lab/terraform.tfstate", owner)
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
    assert store.holder("portfolio/lab/terraform.tfstate") == winners[0]


def test_demo_transfers_lock_after_release() -> None:
    outcome = contend()
    assert outcome["team-a"] == "acquired"
    assert outcome["team-b"].startswith("blocked")
    assert outcome["after_release"] == "team-b"
