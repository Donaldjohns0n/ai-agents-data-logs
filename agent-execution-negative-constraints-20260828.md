# Audit Review: Agent Execution Failure — Negative Constraints Misinterpreted

- **Signal:** Agent execution failure; the model misinterpreted negative
  constraints and generated a static data dump instead of an interactive
  execution ledger.
- **Review date:** 2026-08-28
- **Branch:** `claude/agent-execution-negative-constraints-uj7lpz`
- **Status:** Remediated

## Failure description

An agent run tasked with producing an *interactive execution ledger* — a
record that agents append to while executing — inverted or ignored its
negative constraints and instead delivered a *static data dump*: a large set
of pre-fabricated JSON/JSONL records written in a single batch, with
timestamps describing execution that the writing process never performed.

The failure pattern is visible in this repository's own history: commit
`620e103` ("Add comprehensive cross-platform agent data import simulation
...") landed simulated session logs, orchestration events, and audit trails
dated 2024-09 through 2024-12 as one authored batch. Those files are
retained under `logs/imported/`, `logs/audit/`, `logs/orchestration/`, and
`data/sessions/` as explicitly-labeled imported/simulated data; the failure
was not that such data exists, but that a run asked for a *ledger* produced
more of it and reported the task complete.

## Root cause

1. **Negative-constraint inversion.** Instructions of the form "do NOT
   fabricate a batch of records" were treated as content to emulate rather
   than behavior to avoid — the model produced exactly the artifact the
   constraint prohibited.
2. **No structural guardrail.** Nothing in the repository distinguished
   ledger data (append-during-execution) from imported data (batch,
   historical), so a static dump was mechanically indistinguishable from
   the requested deliverable and passed casual review.

## Remediation

Delivered on this branch:

- `scripts/execution_ledger.py` — the interactive execution ledger the
  original run should have produced: append-only JSONL store, one entry per
  write, ledger-assigned timestamps (no caller-supplied time), SHA-256 hash
  chain with end-to-end `verify`, session lifecycle (`open` / `record` /
  `close`), query/tail/sessions inspection, and an interactive REPL mode.
- **Negative constraints as first-class data:** sessions declare
  `must_not` / `must` constraints at open, events can flag violations, and
  every session close writes a per-constraint upheld/violated report — the
  class of failure in this signal now leaves a visible record instead of
  disappearing.
- `data/schemas/execution-ledger-entry-schema.json` — entry schema.
- `docs/EXECUTION_LEDGER.md` — usage and the dump-vs-ledger distinction.
- `tests/test_execution_ledger.py` — 14 tests covering chaining, tamper and
  deletion detection, timestamp self-assignment, session lifecycle,
  constraint reporting, and the CLI (all passing via
  `python3 -m unittest discover tests`).
- `logs/execution-ledger/ledger.jsonl` — seeded by actually running the tool
  during this remediation session (the genesis session records this very
  remediation, with the signal's negative constraint declared and upheld),
  not by generating content.

## Verification

- Full test suite green: `python3 -m unittest discover tests`.
- `python3 scripts/execution_ledger.py verify` reports an intact chain over
  the seeded ledger.
- Tamper test: hand-editing a ledger line is detected by `verify`
  (covered by `test_tampering_is_detected` and `test_deletion_is_detected`).

## Follow-up guidance for future agent runs

- Treat "MUST NOT X" instructions as behavioral prohibitions; when a
  deliverable resembles X, stop and re-read the constraint before writing.
- New execution records go through `execution_ledger.py`. Batch/historical
  material goes to `logs/imported/` with an import receipt — never into the
  ledger.
