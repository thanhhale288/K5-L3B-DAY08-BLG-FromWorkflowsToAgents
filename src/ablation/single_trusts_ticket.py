"""Ablation for the research card (R2, MAST): shape single with the verification step off.

One variable changes. On seed % 5 == 0, when the delay written in the ticket
disagrees with the order row, the order handed to `compute_compensation` takes the
ticket's number. That is the swarm's REFERENCE_WEAKNESS, moved into the single
agent. Topology, tools, step order, MockLLM calls, seeds, prices and evaluator stay
the same as `lab8.shapes.single`.

Run from src/ (same claims, seeds, prices and evaluator as the main benchmark):

    python -m lab8.benchmark --shapes single,single_trusts_ticket,swarm --extra-shape single_trusts_ticket=ablation.single_trusts_ticket:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_single_ticket_trust.json

Implementation note: this wraps `single.run_claim` and swaps two module globals
(`SHAPE`, `_lock_args`) only for the duration of one call, restoring them in
`finally`. The graded file `lab8/shapes/single.py` carries no ablation switch.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from lab8.db import connect
from lab8.mock_llm import parse_delay_days
from lab8.schemas import RunResult
from lab8.shapes import single
from lab8.tools import get_claim_view

NAME = "single_trusts_ticket"


def _ticket_delay(store_path: str, claim_id: str) -> int | None:
    conn = connect(store_path)
    try:
        claim = get_claim_view(conn, claim_id)
    finally:
        conn.close()
    return parse_delay_days(claim["ticket"]) if claim.get("found") else None


@contextmanager
def _verification_off(ticket_delay: int | None, seed: int) -> Iterator[None]:
    real_lock = single._lock_args
    real_shape = single.SHAPE

    def trusting_lock(name, args, *, claim, collected) -> dict[str, Any]:
        locked = real_lock(name, args, claim=claim, collected=collected)
        if name == "compute_compensation" and ticket_delay is not None and seed % 5 == 0:
            if ticket_delay != int(locked["order"]["delay_days"]):
                locked["order"]["delay_days"] = ticket_delay  # the ablated check
        return locked

    single._lock_args = trusting_lock
    single.SHAPE = NAME
    try:
        yield
    finally:
        single._lock_args = real_lock
        single.SHAPE = real_shape


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    with _verification_off(_ticket_delay(store_path, claim_id), seed):
        return single.run_claim(claim_id, seed=seed, store_path=store_path, crash_at=crash_at)
