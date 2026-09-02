"""Tests for scripts/execution_ledger.py.

Run from the repository root with:
    python3 -m unittest discover tests
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from execution_ledger import (  # noqa: E402
    GENESIS_HASH,
    ExecutionLedger,
    LedgerError,
    main,
)


class LedgerTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "ledger.jsonl")
        self.ledger = ExecutionLedger(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def _open(self, **kwargs):
        kwargs.setdefault("agent_id", "agent-test")
        kwargs.setdefault("task", "unit test task")
        return self.ledger.open_session(**kwargs)


class TestAppendAndChain(LedgerTestCase):
    def test_genesis_entry_links_to_zero_hash(self):
        entry = self._open()
        self.assertEqual(entry["prev_hash"], GENESIS_HASH)
        self.assertEqual(entry["seq"], 1)

    def test_entries_chain_and_verify(self):
        opened = self._open()
        sid = opened["session_id"]
        self.ledger.record_event(sid, "step", "did a thing")
        self.ledger.close_session(sid, "completed", "done")
        entries = self.ledger.entries()
        self.assertEqual([e["seq"] for e in entries], [1, 2, 3])
        self.assertEqual(entries[1]["prev_hash"], entries[0]["entry_hash"])
        self.assertEqual(entries[2]["prev_hash"], entries[1]["entry_hash"])
        ok, problems = self.ledger.verify()
        self.assertTrue(ok, problems)

    def test_ledger_assigns_timestamps_itself(self):
        # There is deliberately no way to pass a timestamp in; whatever the
        # caller stuffs into metadata does not become the entry timestamp.
        entry = self.ledger.record_event(
            self._open()["session_id"], "step", "msg",
            metadata={"timestamp": "1999-01-01T00:00:00Z"},
        )
        self.assertNotEqual(entry["timestamp"], "1999-01-01T00:00:00Z")
        self.assertTrue(entry["timestamp"].endswith("Z"))

    def test_tampering_is_detected(self):
        sid = self._open()["session_id"]
        self.ledger.record_event(sid, "step", "original message")
        lines = open(self.path, encoding="utf-8").read().splitlines()
        doctored = json.loads(lines[1])
        doctored["message"] = "rewritten history"
        lines[1] = json.dumps(doctored, sort_keys=True, separators=(",", ":"))
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        ok, problems = self.ledger.verify()
        self.assertFalse(ok)
        self.assertTrue(any("entry_hash" in p for p in problems))

    def test_deletion_is_detected(self):
        sid = self._open()["session_id"]
        self.ledger.record_event(sid, "step", "one")
        self.ledger.record_event(sid, "step", "two")
        lines = open(self.path, encoding="utf-8").read().splitlines()
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("\n".join([lines[0], lines[2]]) + "\n")
        ok, problems = self.ledger.verify()
        self.assertFalse(ok)


class TestSessionLifecycle(LedgerTestCase):
    def test_record_on_closed_session_is_refused(self):
        sid = self._open()["session_id"]
        self.ledger.close_session(sid, "completed")
        with self.assertRaises(LedgerError):
            self.ledger.record_event(sid, "step", "too late")

    def test_double_close_is_refused(self):
        sid = self._open()["session_id"]
        self.ledger.close_session(sid, "failed", "broke")
        with self.assertRaises(LedgerError):
            self.ledger.close_session(sid, "completed")

    def test_unknown_session_is_refused(self):
        with self.assertRaises(LedgerError):
            self.ledger.record_event("exec-00000000-000000-abcdef", "step", "x")

    def test_sessions_listing(self):
        sid = self._open(task="listing test")["session_id"]
        self.ledger.record_event(sid, "step", "one")
        listing = self.ledger.sessions()
        self.assertEqual(len(listing), 1)
        self.assertEqual(listing[0]["status"], "open")
        self.assertEqual(listing[0]["events"], 1)
        self.ledger.close_session(sid, "completed")
        self.assertEqual(self.ledger.sessions()[0]["status"], "closed")
        self.assertEqual(self.ledger.sessions()[0]["outcome"], "completed")


class TestConstraints(LedgerTestCase):
    def test_negative_constraints_are_declared_and_reported_upheld(self):
        opened = self._open(must_not=["fabricate static data dumps"])
        sid = opened["session_id"]
        self.assertEqual(opened["constraints"][0],
                         {"id": "N1", "kind": "must_not",
                          "text": "fabricate static data dumps"})
        close = self.ledger.close_session(sid, "completed")
        self.assertEqual(close["constraint_report"][0]["status"], "upheld")

    def test_violation_is_flagged_in_close_report(self):
        sid = self._open(must_not=["fabricate static data dumps"])["session_id"]
        bad = self.ledger.record_event(sid, "step", "dumped fake records",
                                       violates=["N1"])
        close = self.ledger.close_session(sid, "failed", "constraint violated")
        report = close["constraint_report"][0]
        self.assertEqual(report["status"], "violated")
        self.assertEqual(report["violating_entries"], [bad["seq"]])

    def test_undeclared_constraint_id_is_refused(self):
        sid = self._open()["session_id"]
        with self.assertRaises(LedgerError):
            self.ledger.record_event(sid, "step", "x", violates=["N9"])


class TestCli(LedgerTestCase):
    def _run(self, *argv):
        return main(["--ledger", self.path] + list(argv))

    def test_full_cli_round_trip(self):
        self.assertEqual(
            self._run("open", "--agent", "agent-cli", "--task", "cli test",
                      "--must-not", "no dumps"), 0)
        sid = self.ledger.sessions()[0]["session_id"]
        self.assertEqual(
            self._run("record", "--session", sid, "--type", "step",
                      "--message", "hello", "--meta", "k=v"), 0)
        self.assertEqual(
            self._run("close", "--session", sid, "--outcome", "completed",
                      "--summary", "ok"), 0)
        self.assertEqual(self._run("verify"), 0)
        self.assertEqual(self._run("sessions"), 0)
        self.assertEqual(self._run("tail", "-n", "5"), 0)
        self.assertEqual(self._run("query", "--session", sid), 0)

    def test_cli_errors_return_nonzero(self):
        self.assertEqual(
            self._run("record", "--session", "exec-00000000-000000-abcdef",
                      "--type", "step", "--message", "x"), 1)


if __name__ == "__main__":
    unittest.main()
