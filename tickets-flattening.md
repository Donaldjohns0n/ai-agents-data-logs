# Tickets: Repository Flattening

Rule in force: **no directory may exist in this repository without a full
ticket in this file.** Rationale source: [failure-doctrine.md](failure-doctrine.md)
("butcher, don't box" — keep stories/relations, not category labels).
Machine-readable edges for every move live in [manifest.json](manifest.json).
The operation is recorded live in the execution ledger, session
`exec-20260902-170823-b2eb2a`.

Ticket format: **what the folder connected** (the wiring it encoded), **where
its contents went**, **why the box was not needed** (the relation survives as
a recorded edge or file content, so the container added nothing but a label).

---

## Kept directories

### T-KEEP-01 — `.git/`
- **What it connects:** every commit to its parent — the full history graph,
  including the pre-flattening hierarchy (recoverable at any commit before
  the flatten) and the `git log --follow` trail across every move.
- **Why it must exist:** it is the version-control substrate, not
  working-tree organization. Removing it would destroy history — the exact
  opposite of "return the bones." It is the one directory whose removal would
  delete relations rather than a label.
- **Status:** KEPT. Not part of the flat working tree; invisible to the file
  layout.

### T-KEEP-02 — `__pycache__/` (ephemeral, intermittent)
- **What it connects:** Python source files to their bytecode cache. Created
  automatically by the interpreter whenever `execution_ledger.py` or the
  tests run without `PYTHONDONTWRITEBYTECODE=1`.
- **Why it is tolerated:** it is generated, gitignored, and self-recreating —
  deleting it is a no-op against the next Python run. `validate.sh` exempts
  fully-gitignored directories from the zero-directory check for this reason,
  and runs its own Python with `PYTHONDONTWRITEBYTECODE=1` so validation does
  not create what it checks for.
- **Status:** EPHEMERAL EXEMPTION. Never committed; safe to delete at any
  time.

---

## Removed directories

Every directory below was removed on 2026-09-02. Files moved by `git mv`
(commit `cc4cad4`: 31 renames, all R100, blob OIDs identical — zero content
bytes changed). Old paths remain resolvable via `git log --follow` and
`manifest.json`.

### T-01 — `agents/` (with `configs/`, `manifests/`, `templates/`)
- **Connected:** agent definitions to their deployment role (config vs
  manifest vs template) — a role already stated inside each file
  (`kind: Agent`, template comments, registry structure).
- **Contents →** `ml-training-agent-config.json`, `agent-registry.json`,
  `data-processing-agent.yaml`, `agent-config-template.yaml` at root.
- **Why no box:** the role lives in the file content and name; the folder
  only repeated it. Its README described subfolders (`runtime/`) that never
  held a single file — a label without contents.
- **Original `agents/README.md` (preserved verbatim):**
  > # Agents Directory
  >
  > Configuration and management files for AI agent orchestration.
  >
  > ## Structure
  > - **configs/**: Agent configuration files and environment settings
  > - **manifests/**: Agent deployment and service manifests
  > - **templates/**: Reusable agent configuration templates
  > - **runtime/**: Runtime state and execution context files
  >
  > ## Agent Management
  > This directory supports: Multi-agent orchestration; Configuration as
  > code; Version-controlled agent definitions; Environment-specific
  > deployments; Service discovery and registration

### T-02 — `audit/` (with `trails/`, `reviews/`)
- **Connected:** audit artifacts to their genre (trail vs review). The
  relation that matters — which events an audit covers — is inside each
  document, not in the path.
- **Contents →** `comprehensive-audit-trail-20241219.json`,
  `cross-agent-orchestration-audit-20240924.json`,
  `agent-execution-negative-constraints-20260828.md` at root.
- **Why no box:** the advertised `assessments/` subfolder never existed on
  disk. The review document cites its own signal and remediation; the trail
  files carry their own correlation ids.
- **Original `audit/README.md` (preserved verbatim):**
  > # Audit Directory
  >
  > Comprehensive audit trails and security assessments.
  >
  > ## Structure
  > - **trails/**: Detailed audit trails and activity logs
  > - **reviews/**: Audit reviews and findings
  > - **assessments/**: Security and compliance assessments
  >
  > ## Audit Capabilities
  > Provides: Complete activity tracking; Change management audit trails;
  > Security event monitoring; Compliance verification; Risk assessment
  > documentation; Forensic investigation support

### T-03 — `compliance/` (with `audit-requirements/`, `policies/`)
- **Connected:** two markdown documents to the word "compliance" — which both
  titles already contain in substance.
- **Contents →** `integrity-verification.md`, `data-governance-policy.md` at
  root.
- **Why no box:** `reports/` and `certifications/` were advertised but never
  existed. Two files do not need three layers of container.
- **Original `compliance/README.md` (preserved verbatim):**
  > # Compliance Directory
  >
  > Regulatory compliance documentation and reporting.
  >
  > ## Structure
  > - **policies/**: Compliance policies and procedures
  > - **reports/**: Regulatory reports and submissions
  > - **certifications/**: Compliance certifications and attestations
  >
  > ## Compliance Framework
  > Supports compliance with: GDPR data protection requirements; SOX
  > financial reporting standards; HIPAA healthcare data protection;
  > Industry-specific regulations; Internal governance policies; Audit trail
  > requirements

### T-04 — `data/` (with `manifests/`, `schemas/`, `sessions/comet-assistant-sessions/`, `sessions/master-quest-sessions/`)
- **Connected:** schemas to the data they validate, and session captures to
  their platform of origin. Both relations are stated inside the files
  (`$id` in schemas; platform fields in session JSON).
- **Contents →** `cross-agent-coordination-manifest.yaml`,
  `agent-manifest-schema.json`, `receipt-schema.json`,
  `execution-ledger-entry-schema.json`, `comet-browser-session-20240920.json`,
  `copilot-session-ai-data-logs-20240924.json` at root.
- **Why no box:** `raw/`, `processed/`, `exports/` were advertised for years
  and never held a file. The deepest path in the repository
  (`data/sessions/master-quest-sessions/…`) encoded platform origin that the
  filename (`copilot-…`) and content already carry.
- **Original `data/README.md` (preserved verbatim):**
  > # Data Directory
  >
  > This directory contains all data storage and management for AI agents.
  >
  > ## Structure
  > - **raw/**: Unprocessed data from agent interactions and operations
  > - **processed/**: Cleaned and transformed data ready for analysis
  > - **schemas/**: JSON schemas and data validation rules
  > - **exports/**: Data exports for reporting and external systems
  >
  > ## Data Governance
  > All data stored here follows strict governance policies: Data retention
  > periods based on compliance requirements; Access controls and permission
  > management; Data classification and sensitivity labels; Audit trails for
  > all data access and modifications

### T-05 — `docs/`
- **Connected:** two documentation files to the label "documentation" — which
  their `.md` extension and titles already announce.
- **Contents →** `EXECUTION_LEDGER.md`, `ORCHESTRATION_AND_COMPLIANCE.md` at
  root (basenames kept).
- **Why no box:** documentation next to what it documents beats documentation
  in a drawer; `EXECUTION_LEDGER.md` now sits beside `execution_ledger.py`.

### T-06 — `logs/` (with `audit/`, `execution-ledger/`, `imported/`, `orchestration/`)
- **Connected:** log streams to their source category. Each stream's identity
  is in its structured content (service, correlation_id, session_id fields) —
  the folders repeated it.
- **Contents →** `ml-training-audit-20241219.jsonl`, `ledger.jsonl`
  (**moved byte-identical; its SHA-256 hash chain verified intact after the
  move**), `copilot-master-quest-pr10-20240924.jsonl`,
  `copilot-session-20240924.jsonl`, `orchestration-events-20240924.jsonl` at
  root.
- **Why no box:** `access/`, `error/`, `performance/` were advertised and
  never existed. The one distinction that matters — live ledger vs imported
  history — is enforced by the ledger's hash chain and recorded in
  `manifest.json`, not by which drawer a file sits in. That distinction
  *failed as a folder* once already (signal
  `agent-execution-negative-constraints`: a static dump passed for a ledger);
  it holds as cryptography.
- **Original `logs/README.md` (preserved verbatim):**
  > # Logs Directory
  >
  > Centralized logging for all AI agent activities and system operations.
  >
  > ## Structure
  > - **access/**: User and system access logs
  > - **audit/**: Security and compliance audit logs
  > - **error/**: Error logs and exception tracking
  > - **performance/**: Performance metrics and monitoring logs
  >
  > ## Log Formats
  > All logs follow structured JSON format for consistent parsing and
  > analysis: ISO 8601 timestamps; Agent identification; Operation context;
  > Severity levels; Correlation IDs for distributed tracing

### T-07 — `provenance/` (with `chains/`, `lineage/`)
- **Connected:** provenance records to their shape (chain vs lineage) — which
  each JSON document declares in its own structure.
- **Contents →** `customer-onboarding-workflow-provenance.json`,
  `sentiment-model-v2.3-lineage.json` at root.
- **Why no box:** `metadata/` was advertised and never existed. Provenance is
  the paradigm case of this doctrine: it is *edges between artifacts*, and
  the folder stored the edges as a label instead.
- **Original `provenance/README.md` (preserved verbatim):**
  > # Provenance Directory
  >
  > Data lineage and provenance tracking for AI agent operations.
  >
  > ## Structure
  > - **chains/**: Operation chains and workflow provenance
  > - **lineage/**: Data lineage and transformation tracking
  > - **metadata/**: Provenance metadata and attribution
  >
  > ## Provenance Tracking
  > Maintains complete audit trail of: Data transformations and processing
  > steps; Agent decision chains; Input/output relationships; Time-series
  > progression; Attribution and responsibility chains; Cross-agent
  > collaboration tracking

### T-08 — `receipts/` (with `transactions/`, `operations/`, `completions/`, `import-receipts/`, `workflow-receipts/`)
- **Connected:** receipts to their transaction type — a field every receipt
  carries internally (`receipt.type`), enforced by `receipt-schema.json`.
- **Contents →** `workflow-completion-certificate-20241219.json`,
  `cross-platform-sync-receipt.json`, `ml-training-receipt-20241219.json`,
  `api-service-call-receipt-20241219.json`, `master-quest-pr10-receipt.json`
  at root.
- **Why no box:** five receipts across five subfolders — one file per drawer.
  The schema, not the drawer, is what makes a receipt a receipt.
- **Original `receipts/README.md` (preserved verbatim):**
  > # Receipts Directory
  >
  > Transaction receipts and operation confirmations with timestamps and
  > agent attribution.
  >
  > ## Structure
  > - **transactions/**: Financial and resource transaction receipts
  > - **operations/**: Operation completion receipts and confirmations
  > - **completions/**: Task and workflow completion certificates
  >
  > ## Receipt Standards
  > All receipts include: Unique receipt IDs; ISO 8601 timestamps; Agent
  > attribution and responsibility; Digital signatures for non-repudiation;
  > Cross-references to related operations; Resource consumption tracking

### T-09 — `scripts/`
- **Connected:** executable tooling to the label "scripts."
- **Contents →** `execution_ledger.py` moved to root.
  `validate-repository.sh` and `validate-imported-data.sh` were **retired,
  not moved**: both existed solely to assert the old folder taxonomy
  (hundreds of hardcoded directory paths, including 11+ directories that
  never existed). They are replaced by `validate.sh`, which validates the
  flat invariant, manifest coverage, hash receipts, the ledger chain, file
  parseability, and the test suite. Their full text is preserved in git
  history (last present at commit `9436ffc`).
- **Why no box:** two of its three files were the taxonomy's enforcement arm;
  the third is the ledger, which belongs beside its data and docs.

### T-10 — `tests/`
- **Connected:** the test module to the label "tests" — which its
  `test_` prefix already carries, and which `unittest` discovery finds by
  pattern, not by folder.
- **Contents →** `test_execution_ledger.py` at root
  (`python3 -m unittest discover -s . -p "test_*.py"`).

---

## Standing rule for future work

Adding a directory to this repository requires adding a full keep-ticket to
this file **in the same commit**, stating what the directory connects that
file content and `manifest.json` edges cannot. `validate.sh` fails on any
unticketed, non-gitignored directory.
