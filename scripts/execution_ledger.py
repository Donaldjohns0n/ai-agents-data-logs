#!/usr/bin/env python3
"""Interactive execution ledger for AI agent sessions.

This tool is the remediation for signal ``agent-execution-negative-constraints``:
a prior agent run was asked for an interactive execution ledger, misread the
negative constraints, and batch-fabricated a static data dump instead. The
ledger below is built so that failure mode is structurally impossible to
repeat quietly:

- Entries are appended one at a time, as execution actually happens. There is
  no bulk-import path; historical/simulated data belongs in ``logs/imported/``,
  never here.
- The ledger assigns every timestamp itself at append time. Callers cannot
  supply timestamps, so records cannot be back-dated to fake a history.
- Entries form a SHA-256 hash chain (each entry commits to its predecessor),
  so any retroactive edit, deletion, or reordering is detectable by
  ``verify``.
- Negative constraints ("the agent MUST NOT ...") are first-class: they are
  declared when a session opens, individual events can flag violations, and
  the closing entry carries a constraint report so misinterpretation is
  visible in the record rather than lost.

Usage:
    execution_ledger.py open --agent <id> --task <text> [--must-not <text>]...
                             [--must <text>]...
    execution_ledger.py record --session <id> --type <event_type>
                               --message <text> [--meta k=v]...
                               [--violates <constraint_id>]...
    execution_ledger.py close --session <id> --outcome completed|failed
                              [--summary <text>]
    execution_ledger.py sessions | tail [-n N] | query [...] | verify
    execution_ledger.py interactive

The store is ``logs/execution-ledger/ledger.jsonl`` relative to the repo root
(override with --ledger). Entries validate against
``data/schemas/execution-ledger-entry-schema.json``.
"""

import argparse
import datetime as _dt
import hashlib
import json
import os
import shlex
import sys
import uuid

GENESIS_HASH = "0" * 64
LEDGER_VERSION = "1.0"
DEFAULT_LEDGER = os.path.join("logs", "execution-ledger", "ledger.jsonl")

ENTRY_TYPES = ("session_open", "event", "session_close")
OUTCOMES = ("completed", "failed")


class LedgerError(Exception):
    """Raised for integrity violations and invalid ledger operations."""


def _utc_now():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _canonical(entry):
    """Canonical JSON serialization used for hashing (entry_hash excluded)."""
    hashable = {k: v for k, v in entry.items() if k != "entry_hash"}
    return json.dumps(hashable, sort_keys=True, separators=(",", ":"))


def _entry_hash(entry):
    return hashlib.sha256(_canonical(entry).encode("utf-8")).hexdigest()


def _repo_root():
    """Walk upward from this script to the repository root."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


class ExecutionLedger:
    """Append-only, hash-chained execution ledger stored as JSONL."""

    def __init__(self, path):
        self.path = path

    # -- storage ----------------------------------------------------------

    def entries(self):
        if not os.path.exists(self.path):
            return []
        loaded = []
        with open(self.path, "r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    loaded.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise LedgerError(
                        "ledger line %d is not valid JSON: %s" % (lineno, exc)
                    )
        return loaded

    def _append(self, entry):
        """Stamp, chain, and persist exactly one entry. The single write path."""
        existing = self.entries()
        entry["seq"] = len(existing) + 1
        entry["timestamp"] = _utc_now()  # ledger-assigned; never caller-supplied
        entry["ledger_version"] = LEDGER_VERSION
        entry["prev_hash"] = existing[-1]["entry_hash"] if existing else GENESIS_HASH
        entry["entry_hash"] = _entry_hash(entry)
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")
        return entry

    # -- session state ----------------------------------------------------

    def _session_entries(self, session_id):
        found = [e for e in self.entries() if e.get("session_id") == session_id]
        if not found:
            raise LedgerError("unknown session: %s" % session_id)
        return found

    def session_state(self, session_id):
        found = self._session_entries(session_id)
        closed = any(e["entry_type"] == "session_close" for e in found)
        return "closed" if closed else "open"

    def session_constraints(self, session_id):
        opener = self._session_entries(session_id)[0]
        return opener.get("constraints", [])

    # -- operations -------------------------------------------------------

    def open_session(self, agent_id, task, must_not=(), must=(), metadata=None):
        constraints = []
        for i, text in enumerate(must_not, 1):
            constraints.append({"id": "N%d" % i, "kind": "must_not", "text": text})
        for i, text in enumerate(must, 1):
            constraints.append({"id": "P%d" % i, "kind": "must", "text": text})
        session_id = "exec-%s-%s" % (
            _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d-%H%M%S"),
            uuid.uuid4().hex[:6],
        )
        entry = {
            "entry_type": "session_open",
            "session_id": session_id,
            "agent": {"id": agent_id},
            "task": task,
            "constraints": constraints,
            "metadata": metadata or {},
        }
        return self._append(entry)

    def record_event(self, session_id, event_type, message, metadata=None,
                     violates=()):
        if self.session_state(session_id) == "closed":
            raise LedgerError("session %s is closed; open a new session" % session_id)
        known = {c["id"] for c in self.session_constraints(session_id)}
        unknown = [v for v in violates if v not in known]
        if unknown:
            raise LedgerError(
                "constraint id(s) %s not declared by session %s"
                % (", ".join(unknown), session_id)
            )
        entry = {
            "entry_type": "event",
            "session_id": session_id,
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
        }
        if violates:
            entry["violates"] = list(violates)
        return self._append(entry)

    def close_session(self, session_id, outcome, summary=""):
        if outcome not in OUTCOMES:
            raise LedgerError("outcome must be one of: %s" % ", ".join(OUTCOMES))
        if self.session_state(session_id) == "closed":
            raise LedgerError("session %s is already closed" % session_id)
        found = self._session_entries(session_id)
        violated = {}
        for e in found:
            for cid in e.get("violates", []):
                violated.setdefault(cid, []).append(e["seq"])
        report = []
        for c in self.session_constraints(session_id):
            report.append({
                "id": c["id"],
                "kind": c["kind"],
                "text": c["text"],
                "status": "violated" if c["id"] in violated else "upheld",
                "violating_entries": violated.get(c["id"], []),
            })
        entry = {
            "entry_type": "session_close",
            "session_id": session_id,
            "outcome": outcome,
            "summary": summary,
            "constraint_report": report,
            "events_recorded": sum(1 for e in found if e["entry_type"] == "event"),
        }
        return self._append(entry)

    # -- inspection -------------------------------------------------------

    def verify(self):
        """Re-derive the hash chain; return (ok, problems)."""
        problems = []
        prev = GENESIS_HASH
        for i, entry in enumerate(self.entries(), 1):
            if entry.get("seq") != i:
                problems.append("entry %d: seq is %r, expected %d" % (i, entry.get("seq"), i))
            if entry.get("prev_hash") != prev:
                problems.append("entry %d: broken chain (prev_hash mismatch)" % i)
            if entry.get("entry_hash") != _entry_hash(entry):
                problems.append("entry %d: content does not match entry_hash" % i)
            if entry.get("entry_type") not in ENTRY_TYPES:
                problems.append("entry %d: unknown entry_type %r" % (i, entry.get("entry_type")))
            prev = entry.get("entry_hash", "")
        return (not problems, problems)

    def sessions(self):
        state = {}
        for e in self.entries():
            sid = e.get("session_id")
            if e["entry_type"] == "session_open":
                state[sid] = {
                    "session_id": sid,
                    "agent": e["agent"]["id"],
                    "task": e.get("task", ""),
                    "opened": e["timestamp"],
                    "status": "open",
                    "outcome": None,
                    "events": 0,
                }
            elif sid in state and e["entry_type"] == "event":
                state[sid]["events"] += 1
            elif sid in state and e["entry_type"] == "session_close":
                state[sid]["status"] = "closed"
                state[sid]["outcome"] = e["outcome"]
        return list(state.values())

    def query(self, session=None, agent=None, entry_type=None, event_type=None):
        agents = {}
        for e in self.entries():
            if e["entry_type"] == "session_open":
                agents[e["session_id"]] = e["agent"]["id"]
        results = []
        for e in self.entries():
            if session and e.get("session_id") != session:
                continue
            if agent and agents.get(e.get("session_id")) != agent:
                continue
            if entry_type and e["entry_type"] != entry_type:
                continue
            if event_type and e.get("event_type") != event_type:
                continue
            results.append(e)
        return results


# -- presentation ---------------------------------------------------------

def _format_entry(e):
    if e["entry_type"] == "session_open":
        detail = "OPEN  agent=%s task=%s" % (e["agent"]["id"], e.get("task", ""))
        if e.get("constraints"):
            detail += " constraints=%d" % len(e["constraints"])
    elif e["entry_type"] == "session_close":
        detail = "CLOSE outcome=%s %s" % (e["outcome"], e.get("summary", ""))
        bad = [c["id"] for c in e.get("constraint_report", []) if c["status"] == "violated"]
        if bad:
            detail += " VIOLATED=%s" % ",".join(bad)
    else:
        detail = "%-18s %s" % (e.get("event_type", ""), e.get("message", ""))
        if e.get("violates"):
            detail += " [violates %s]" % ",".join(e["violates"])
    return "%4d  %s  %s  %s" % (e["seq"], e["timestamp"], e.get("session_id", "-"), detail)


def _parse_meta(pairs):
    meta = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise LedgerError("--meta expects key=value, got %r" % pair)
        key, value = pair.split("=", 1)
        meta[key] = value
    return meta


# -- interactive mode -----------------------------------------------------

INTERACTIVE_HELP = """Commands:
  open <agent_id> <task...>                 open a session (declare
        constraints via the CLI 'open --must-not/--must' when needed)
  record <session_id> <event_type> <message...>   append one event
  close <session_id> <completed|failed> [summary...]
  sessions | tail [n] | verify | help | quit
"""


def interactive(ledger):
    print("execution-ledger interactive mode (ledger: %s)" % ledger.path)
    print("type 'help' for commands, 'quit' to exit")
    while True:
        try:
            raw = input("ledger> ").strip()
        except EOFError:
            print()
            return 0
        if not raw:
            continue
        try:
            parts = shlex.split(raw)
        except ValueError as exc:
            print("parse error: %s" % exc)
            continue
        cmd, args = parts[0], parts[1:]
        try:
            if cmd in ("quit", "exit"):
                return 0
            elif cmd == "help":
                print(INTERACTIVE_HELP)
            elif cmd == "open":
                if len(args) < 2:
                    print("usage: open <agent_id> <task...>")
                    continue
                entry = ledger.open_session(args[0], " ".join(args[1:]))
                print("opened %s" % entry["session_id"])
            elif cmd == "record":
                if len(args) < 3:
                    print("usage: record <session_id> <event_type> <message...>")
                    continue
                entry = ledger.record_event(args[0], args[1], " ".join(args[2:]))
                print("recorded seq %d" % entry["seq"])
            elif cmd == "close":
                if len(args) < 2:
                    print("usage: close <session_id> <completed|failed> [summary...]")
                    continue
                entry = ledger.close_session(args[0], args[1], " ".join(args[2:]))
                print("closed %s (%s)" % (args[0], entry["outcome"]))
            elif cmd == "sessions":
                for s in ledger.sessions():
                    print("%s  %-6s  agent=%s events=%d  %s"
                          % (s["session_id"], s["status"], s["agent"], s["events"], s["task"]))
            elif cmd == "tail":
                n = int(args[0]) if args else 10
                for e in ledger.entries()[-n:]:
                    print(_format_entry(e))
            elif cmd == "verify":
                ok, problems = ledger.verify()
                print("chain OK (%d entries)" % len(ledger.entries()) if ok
                      else "\n".join(problems))
            else:
                print("unknown command %r; type 'help'" % cmd)
        except LedgerError as exc:
            print("error: %s" % exc)


# -- CLI ------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="execution_ledger.py",
        description="Append-only, hash-chained, interactive execution ledger "
                    "for AI agent sessions.",
    )
    parser.add_argument(
        "--ledger",
        default=os.path.join(_repo_root(), DEFAULT_LEDGER),
        help="path to the ledger JSONL file (default: %(default)s)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_open = sub.add_parser("open", help="open a new execution session")
    p_open.add_argument("--agent", required=True, help="agent identifier")
    p_open.add_argument("--task", required=True, help="what this session is doing")
    p_open.add_argument("--must-not", action="append", default=[], dest="must_not",
                        metavar="TEXT", help="negative constraint (repeatable)")
    p_open.add_argument("--must", action="append", default=[],
                        metavar="TEXT", help="positive constraint (repeatable)")
    p_open.add_argument("--meta", action="append", default=[], metavar="K=V")

    p_rec = sub.add_parser("record", help="append one event to an open session")
    p_rec.add_argument("--session", required=True)
    p_rec.add_argument("--type", required=True, dest="event_type",
                       help="event type, e.g. step, tool_call, decision, error")
    p_rec.add_argument("--message", required=True)
    p_rec.add_argument("--meta", action="append", default=[], metavar="K=V")
    p_rec.add_argument("--violates", action="append", default=[],
                       metavar="CONSTRAINT_ID",
                       help="declared constraint this event violated (repeatable)")

    p_close = sub.add_parser("close", help="close a session with an outcome")
    p_close.add_argument("--session", required=True)
    p_close.add_argument("--outcome", required=True, choices=OUTCOMES)
    p_close.add_argument("--summary", default="")

    sub.add_parser("sessions", help="list sessions and their status")

    p_tail = sub.add_parser("tail", help="show the most recent entries")
    p_tail.add_argument("-n", type=int, default=10)

    p_query = sub.add_parser("query", help="filter entries; prints JSONL")
    p_query.add_argument("--session")
    p_query.add_argument("--agent")
    p_query.add_argument("--entry-type", choices=ENTRY_TYPES)
    p_query.add_argument("--event-type")

    sub.add_parser("verify", help="verify the hash chain end to end")
    sub.add_parser("interactive", help="start an interactive REPL")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    ledger = ExecutionLedger(args.ledger)
    try:
        if args.command == "open":
            entry = ledger.open_session(args.agent, args.task,
                                        must_not=args.must_not, must=args.must,
                                        metadata=_parse_meta(args.meta))
            print(entry["session_id"])
        elif args.command == "record":
            entry = ledger.record_event(args.session, args.event_type, args.message,
                                        metadata=_parse_meta(args.meta),
                                        violates=args.violates)
            print("seq %d" % entry["seq"])
        elif args.command == "close":
            entry = ledger.close_session(args.session, args.outcome, args.summary)
            violated = [c["id"] for c in entry["constraint_report"]
                        if c["status"] == "violated"]
            print("closed %s outcome=%s%s"
                  % (args.session, args.outcome,
                     " violated=%s" % ",".join(violated) if violated else ""))
        elif args.command == "sessions":
            for s in ledger.sessions():
                print("%s  %-6s  agent=%s events=%d  %s"
                      % (s["session_id"], s["status"], s["agent"], s["events"], s["task"]))
        elif args.command == "tail":
            for e in ledger.entries()[-args.n:]:
                print(_format_entry(e))
        elif args.command == "query":
            for e in ledger.query(session=args.session, agent=args.agent,
                                  entry_type=args.entry_type,
                                  event_type=args.event_type):
                print(json.dumps(e, sort_keys=True, separators=(",", ":")))
        elif args.command == "verify":
            ok, problems = ledger.verify()
            if ok:
                print("chain OK (%d entries)" % len(ledger.entries()))
            else:
                for p in problems:
                    print(p)
                return 1
        elif args.command == "interactive":
            return interactive(ledger)
    except LedgerError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
