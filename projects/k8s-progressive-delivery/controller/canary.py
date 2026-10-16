"""Canary promotion decisions for checkout-api.

Control flow matches docs/architecture/sources/05-canary-rollback-sequence.mmd:

- deploy the candidate at 10 percent ingress weight
- if checkout_synthetic_error_rate stays under the threshold, shift to 50 then 100
- at 100 percent, scale the previous stable revision to zero
- if the error rate reaches the threshold, send all traffic to stable and scale the canary to zero
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

# Sequence diagram steps: 10% → 50% → 100%.
PROMOTION_WEIGHTS: tuple[int, ...] = (10, 50, 100)
DEFAULT_ERROR_THRESHOLD = 0.05
DEFAULT_MIN_SAMPLES = 20


@dataclass(frozen=True)
class RolloutState:
    stable_revision: str
    canary_revision: str
    canary_weight: int
    stable_replicas: int
    canary_replicas: int


@dataclass(frozen=True)
class Signal:
    error_rate: float
    sample_count: int


@dataclass(frozen=True)
class Decision:
    action: str
    canary_weight: int
    stable_replicas: int
    canary_replicas: int
    reason: str

    @property
    def rolled_back(self) -> bool:
        return self.action == "rollback"


def next_weight(current: int) -> int | None:
    for weight in PROMOTION_WEIGHTS:
        if weight > current:
            return weight
    return None


def decide(
    state: RolloutState,
    signal: Signal,
    *,
    threshold: float = DEFAULT_ERROR_THRESHOLD,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> Decision:
    if min_samples < 1:
        raise ValueError("min_samples must be at least 1")
    if signal.sample_count < min_samples:
        return Decision(
            action="hold",
            canary_weight=state.canary_weight,
            stable_replicas=state.stable_replicas,
            canary_replicas=state.canary_replicas,
            reason=f"insufficient samples ({signal.sample_count} < {min_samples})",
        )
    if signal.error_rate >= threshold:
        return Decision(
            action="rollback",
            canary_weight=0,
            stable_replicas=state.stable_replicas,
            canary_replicas=0,
            reason=(
                f"error_rate {signal.error_rate:.4f} >= threshold {threshold:.4f}; "
                "send 100% to stable and scale canary to 0"
            ),
        )
    upcoming = next_weight(state.canary_weight)
    if upcoming is None or upcoming == 100:
        return Decision(
            action="promote",
            canary_weight=100,
            stable_replicas=0,
            canary_replicas=max(state.stable_replicas, state.canary_replicas, 1),
            reason="error_rate below threshold; shift 100% to canary and scale the old revision to 0",
        )
    return Decision(
        action="promote",
        canary_weight=upcoming,
        stable_replicas=state.stable_replicas,
        canary_replicas=state.canary_replicas,
        reason=f"error_rate below threshold; shift canary weight to {upcoming}%",
    )


def ingress_canary_annotations(weight: int) -> dict[str, str]:
    """nginx ingress canary annotations. Weight 0 removes the canary ingress."""
    if weight <= 0:
        return {}
    if weight > 100:
        raise ValueError("canary weight must be between 0 and 100")
    return {
        "nginx.ingress.kubernetes.io/canary": "true",
        "nginx.ingress.kubernetes.io/canary-weight": str(weight),
    }


def run_promotion(
    *,
    error_rate: float,
    samples_per_step: int = 50,
    threshold: float = DEFAULT_ERROR_THRESHOLD,
    starting_weight: int = 10,
) -> list[Decision]:
    """Walk the evaluate loop until the candidate is fully promoted or rolled back."""
    state = RolloutState(
        stable_revision="vN",
        canary_revision="vN+1",
        canary_weight=starting_weight,
        stable_replicas=2,
        canary_replicas=1,
    )
    decisions: list[Decision] = []
    for _ in range(len(PROMOTION_WEIGHTS) + 1):
        decision = decide(
            state,
            Signal(error_rate=error_rate, sample_count=samples_per_step),
            threshold=threshold,
        )
        decisions.append(decision)
        state = RolloutState(
            stable_revision=state.stable_revision,
            canary_revision=state.canary_revision,
            canary_weight=decision.canary_weight,
            stable_replicas=decision.stable_replicas,
            canary_replicas=decision.canary_replicas,
        )
        if decision.action == "rollback":
            break
        if decision.action == "hold":
            break
        if decision.canary_weight == 100 and decision.stable_replicas == 0:
            break
    return decisions


def _print_decisions(decisions: list[Decision]) -> None:
    for index, decision in enumerate(decisions, start=1):
        print(
            json.dumps(
                {
                    "step": index,
                    **asdict(decision),
                }
            )
        )


def demo(mode: str) -> int:
    if mode == "promote":
        decisions = run_promotion(error_rate=0.0)
        final = decisions[-1]
        ok = (
            [item.canary_weight for item in decisions] == [50, 100]
            and final.action == "promote"
            and final.stable_replicas == 0
            and final.canary_weight == 100
        )
    elif mode == "rollback":
        decisions = run_promotion(error_rate=0.4)
        final = decisions[-1]
        ok = (
            len(decisions) == 1
            and final.action == "rollback"
            and final.canary_weight == 0
            and final.canary_replicas == 0
            and final.stable_replicas == 2
        )
    else:
        raise ValueError(f"unknown mode {mode}")
    _print_decisions(decisions)
    if not ok:
        print(f"demo {mode} did not match the canary sequence", flush=True)
        return 1
    print(f"demo {mode} matched the canary sequence")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Checkout canary controller")
    sub = parser.add_subparsers(dest="command", required=True)

    demo_parser = sub.add_parser("demo", help="run the promote or rollback path")
    demo_parser.add_argument("--mode", choices=("promote", "rollback"), required=True)

    decide_parser = sub.add_parser("decide", help="print one decision as JSON")
    decide_parser.add_argument("--error-rate", type=float, required=True)
    decide_parser.add_argument("--weight", type=int, default=10)
    decide_parser.add_argument("--samples", type=int, default=50)
    decide_parser.add_argument("--threshold", type=float, default=DEFAULT_ERROR_THRESHOLD)

    args = parser.parse_args(argv)
    if args.command == "demo":
        return demo(args.mode)

    decision = decide(
        RolloutState("vN", "vN+1", args.weight, 2, 1),
        Signal(args.error_rate, args.samples),
        threshold=args.threshold,
    )
    print(json.dumps(asdict(decision)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
