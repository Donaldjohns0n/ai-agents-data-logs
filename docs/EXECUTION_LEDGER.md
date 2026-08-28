# Interactive Execution Ledger

`scripts/execution_ledger.py` is the live, append-only record of agent
execution in this repository. Agents (or their operators) write to it **while
work is happening**, one entry at a time; they do not deposit pre-built
histories into it. The ledger store is `logs/execution-ledger/ledger.jsonl`,
and every entry validates against
`data/schemas/execution-ledger-entry-schema.json`.

## Why this exists

Remediation for signal **agent-execution-negative-constraints** (recorded in
`audit/reviews/agent-execution-negative-constraints-20260828.md`): an agent
run asked to produce an interactive execution ledger misinterpreted its
negative constraints and instead batch-generated a static data dump —
plausible-looking records fabricated in one shot with invented timestamps.

A static dump and a ledger are opposites. A dump is written once, after (or
instead of) the fact, and can say anything. A ledger accretes during
execution, and each entry is evidence that a specific step actually happened
at a specific time. This tool makes the dump failure mode structurally hard
to repeat:

| Failure mode in the signal | Structural countermeasure |
| --- | --- |
| Records fabricated in one batch | No bulk-import path; the only write operation appends exactly one entry. Imported/simulated history belongs in `logs/imported/`, never here. |
| Invented timestamps | The ledger stamps every entry with its own UTC clock at append time; callers cannot supply a timestamp. |
| Silent rewriting of history | SHA-256 hash chain: each entry commits to its predecessor. `verify` detects edits, deletions, and reordering. |
| Negative constraints ignored | Constraints (`must_not` / `must`) are declared at session open, events can flag violations, and every session close carries a per-constraint upheld/violated report. Misinterpretation becomes a visible record instead of a quiet failure. |

## Usage

Open a session when an agent starts a task, declaring its constraints:

```bash
python3 scripts/execution_ledger.py open \
  --agent agent-claude-code \
  --task "Refactor the receipt validator" \
  --must-not "fabricate records not produced by real execution" \
  --must "record each material step as it happens"
# prints the session id, e.g. exec-20260828-153000-a1b2c3
```

Record events one at a time, as they happen:

```bash
python3 scripts/execution_ledger.py record \
  --session exec-20260828-153000-a1b2c3 \
  --type tool_call --message "ran unit tests" --meta result=pass

# if a declared constraint was violated, say so — that is the point:
python3 scripts/execution_ledger.py record \
  --session exec-20260828-153000-a1b2c3 \
  --type error --message "wrote records without executing" --violates N1
```

Close the session with an outcome; the close entry includes the constraint
report:

```bash
python3 scripts/execution_ledger.py close \
  --session exec-20260828-153000-a1b2c3 \
  --outcome completed --summary "validator refactored, tests green"
```

Inspect and verify:

```bash
python3 scripts/execution_ledger.py sessions        # session list + status
python3 scripts/execution_ledger.py tail -n 20      # recent entries, readable
python3 scripts/execution_ledger.py query --session exec-... # filtered JSONL
python3 scripts/execution_ledger.py verify          # end-to-end hash chain
```

Or drive it interactively:

```bash
python3 scripts/execution_ledger.py interactive
ledger> open agent-claude-code investigate flaky test
ledger> record exec-... step reproduced the failure locally
ledger> close exec-... completed root cause fixed
ledger> verify
```

## Entry format

Every entry carries `seq`, a ledger-assigned `timestamp`, `entry_type`
(`session_open` | `event` | `session_close`), `session_id`, `prev_hash`, and
`entry_hash` (SHA-256 over the entry's canonical JSON with `entry_hash`
removed; the genesis entry's `prev_hash` is 64 zeros). See the schema for the
type-specific fields.

## Rules

1. **Append during execution, never after the fact.** If work happened and
   was not recorded, record it now with an honest message — the timestamp
   will show when it was actually written, and that is correct behavior.
2. **One event per entry.** Generating many entries in a loop to simulate a
   history is the exact failure this ledger remediates.
3. **Never edit `ledger.jsonl` by hand.** `verify` will flag it; a broken
   chain is an incident, not a cleanup task.
4. **Declare negative constraints at open.** A session with no declared
   constraints cannot report on them.

## Tests

```bash
python3 -m unittest discover tests
```
