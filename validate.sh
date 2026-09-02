#!/bin/bash
# Flat-repository validator. Replaces the retired taxonomy validators
# (validate-repository.sh, validate-imported-data.sh — see
# tickets-flattening.md T-09).
#
# Checks:
#   1. Zero directories besides .git (fully-gitignored dirs exempt, per
#      ticket T-KEEP-02)
#   2. Every tracked file appears in manifest.json, and vice versa
#   3. post_sha256 receipts match for every non-null entry (ledger exempt)
#   4. Ledger prefix receipt: the recorded first N lines still hash to the
#      recorded value (pre-existing content moved, never edited)
#   5. Ledger hash chain verifies end to end
#   6. Every .json parses; every .jsonl parses line by line; .yaml if PyYAML
#   7. Test suite passes

set -u
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "PASS: $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL: $1"; }

# 1. Flat invariant
UNTICKETED=""
while IFS= read -r d; do
    if ! git check-ignore -q "$d"; then
        UNTICKETED="$UNTICKETED $d"
    fi
done < <(find . -mindepth 1 -type d -not -path './.git' -not -path './.git/*')
if [ -z "$UNTICKETED" ]; then
    ok "flat invariant: no unticketed directories"
else
    bad "unticketed directories present (need a keep-ticket in tickets-flattening.md):$UNTICKETED"
fi

# 2-4. Manifest coverage, hash receipts, ledger prefix
python3 - <<'EOF'
import hashlib, json, subprocess, sys

manifest = json.load(open("manifest.json"))
files = {f["new_path"]: f for f in manifest["files"]}
tracked = set(subprocess.run(["git", "ls-files"], capture_output=True,
                             text=True, check=True).stdout.split())

failures = []
missing = tracked - set(files)
extra = {p for p, f in files.items()
         if f["status"] not in ("merged_deleted", "deleted", "replaced")} - tracked
if missing:
    failures.append("tracked files absent from manifest: %s" % sorted(missing))
if extra:
    failures.append("manifest lists nonexistent files: %s" % sorted(extra))

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

for path, entry in files.items():
    if path == "ledger.jsonl" or entry.get("post_sha256") is None:
        continue
    if entry["status"] in ("merged_deleted", "deleted", "replaced"):
        continue
    actual = sha256(path)
    if actual != entry["post_sha256"]:
        failures.append("hash mismatch: %s" % path)

led = manifest["ledger_exception"]
lines = open("ledger.jsonl", "rb").read().splitlines(keepends=True)
n = led["post_prefix_lines"]
prefix_hash = hashlib.sha256(b"".join(lines[:n])).hexdigest()
if prefix_hash != led["post_prefix_sha256"]:
    failures.append("ledger prefix receipt mismatch (first %d lines)" % n)

if failures:
    for f in failures:
        print("FAIL: " + f)
    sys.exit(1)
print("PASS: manifest coverage (%d tracked files)" % len(tracked))
print("PASS: hash receipts match for all non-ledger files")
print("PASS: ledger prefix receipt (first %d lines)" % n)
EOF
if [ $? -eq 0 ]; then PASS=$((PASS+3)); else FAIL=$((FAIL+1)); fi

# 5. Ledger chain
if python3 execution_ledger.py verify >/dev/null; then
    ok "ledger hash chain verifies"
else
    bad "ledger hash chain broken"
fi

# 6. Parse checks
python3 - <<'EOF'
import glob, json, sys
failures = []
for path in glob.glob("*.json"):
    try:
        json.load(open(path))
    except Exception as exc:
        failures.append("%s: %s" % (path, exc))
for path in glob.glob("*.jsonl"):
    for i, line in enumerate(open(path), 1):
        if line.strip():
            try:
                json.loads(line)
            except Exception as exc:
                failures.append("%s line %d: %s" % (path, i, exc))
try:
    import yaml
    for path in glob.glob("*.yaml"):
        try:
            yaml.safe_load(open(path))
        except Exception as exc:
            failures.append("%s: %s" % (path, exc))
except ImportError:
    print("NOTE: PyYAML not installed; YAML files not checked")
if failures:
    for f in failures:
        print("FAIL: " + f)
    sys.exit(1)
print("PASS: all JSON/JSONL (and YAML if available) files parse")
EOF
if [ $? -eq 0 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi

# 7. Tests
if python3 -m unittest discover -s . -p 'test_*.py' >/dev/null 2>&1; then
    ok "test suite passes"
else
    bad "test suite failing"
fi

echo "----------------------------------------"
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]
