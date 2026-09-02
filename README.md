# AI Agents Data and Logs Repository

Dedicated repository for AI agents data storage, audit logs, provenance tracking, and cross-agent orchestration. This serves as the source-of-truth for all agent activity and compliance records in our multi-agent AI ecosystem.

## 🚀 Overview

This repository implements a comprehensive data governance and orchestration framework for AI agents, providing:

- **Flat, Relation-Mapped Layout**: Files live at the repository root; the former folder hierarchy is preserved as recorded relations in [manifest.json](manifest.json), not as boxes (see [failure-doctrine.md](failure-doctrine.md) — "butcher, don't box")
- **Agent Tracking Manifests**: JSON/YAML configurations for agent deployment and monitoring
- **Receipt System**: Timestamped transaction receipts with agent attribution
- **Data Governance**: Comprehensive policies and compliance framework
- **Cross-Agent Orchestration**: Multi-agent workflow coordination and management

## 📁 Repository Layout

The repository is intentionally flat: **no directories** (only `.git`, ticketed in [tickets-flattening.md](tickets-flattening.md)). Every file's former path and the reason its folder was removed are recorded in [manifest.json](manifest.json) and [tickets-flattening.md](tickets-flattening.md). The file families below absorb what the old per-folder READMEs described.

### Execution ledger (live agent activity)
- `execution_ledger.py` — the interactive, append-only, hash-chained execution ledger CLI
- `ledger.jsonl` — the ledger store (never edit by hand; only the tool appends)
- `execution-ledger-entry-schema.json` — entry schema
- `EXECUTION_LEDGER.md` — usage documentation
- `test_execution_ledger.py` — test suite (`python3 -m unittest discover -s . -p "test_*.py"`)

### Agent configuration and management
Multi-agent orchestration, configuration as code, version-controlled agent definitions:
- `agent-config-template.yaml` — reusable agent configuration template
- `ml-training-agent-config.json` — agent configuration and environment settings
- `agent-registry.json`, `data-processing-agent.yaml` — deployment and service manifests

### Schemas and validation
- `agent-manifest-schema.json`, `receipt-schema.json`, `execution-ledger-entry-schema.json`
- `validate.sh` — repository validator (flat invariant, manifest coverage, hashes, ledger chain, parsing, tests)

### Logs (structured JSON: ISO 8601 timestamps, agent identification, correlation IDs)
- `ml-training-audit-20241219.jsonl` — security/compliance audit log
- `copilot-master-quest-pr10-20240924.jsonl`, `copilot-session-20240924.jsonl` — imported historical sessions
- `orchestration-events-20240924.jsonl` — cross-agent orchestration events

### Session data
- `comet-browser-session-20240920.json`, `copilot-session-ai-data-logs-20240924.json`
- `cross-agent-coordination-manifest.yaml`

### Receipts (unique IDs, timestamps, agent attribution, signatures, cross-references)
- `api-service-call-receipt-20241219.json` — transaction receipt
- `ml-training-receipt-20241219.json` — operation completion receipt
- `workflow-completion-certificate-20241219.json` — workflow completion certificate
- `cross-platform-sync-receipt.json`, `master-quest-pr10-receipt.json` — import/workflow receipts

### Provenance (transformations, decision chains, input/output relationships, attribution)
- `customer-onboarding-workflow-provenance.json` — operation chain / workflow provenance
- `sentiment-model-v2.3-lineage.json` — data transformation lineage

### Audit (activity tracking, compliance verification, forensic support)
- `comprehensive-audit-trail-20241219.json`, `cross-agent-orchestration-audit-20240924.json` — audit trails
- `agent-execution-negative-constraints-20260828.md` — audit review of the negative-constraints failure signal

### Compliance (GDPR, SOX, HIPAA, internal governance)
- `data-governance-policy.md` — policies and procedures
- `integrity-verification.md` — audit requirements / integrity verification

### Governance of this layout itself
- `failure-doctrine.md` — the ten rules, playbook, and constitution the flat layout implements
- `tickets-flattening.md` — one full ticket per removed directory, plus the `.git` keep-ticket
- `manifest.json` — old path → new path edges with SHA-256 receipts for the flattening
- `ORCHESTRATION_AND_COMPLIANCE.md` — technical orchestration documentation
- `CONTRIBUTING.md` — data governance policies and contribution process

## 🛠️ Key Features

### 1. Multi-Agent Orchestration
- **Workflow Engine**: Support for sequential, parallel, and event-driven workflows
- **Service Discovery**: Automatic agent registration and service mesh integration
- **Load Balancing**: Intelligent request distribution across agent instances
- **Circuit Breaker**: Fault tolerance and graceful degradation

### 2. Comprehensive Audit System
- **Complete Audit Trails**: Every agent operation is tracked and logged
- **Compliance Monitoring**: Real-time compliance verification and reporting
- **Data Lineage**: Full provenance tracking from input to output
- **Transaction Receipts**: Cryptographically signed operation confirmations

### 3. Data Governance Framework
- **Data Classification**: Automatic classification based on content and context
- **Retention Policies**: Configurable data lifecycle management
- **Access Controls**: Fine-grained permission management
- **Privacy Protection**: GDPR, CCPA, and other privacy regulation compliance

### 4. Security and Compliance
- **Zero Trust Architecture**: Never trust, always verify approach
- **Encryption**: End-to-end encryption for data in transit and at rest
- **Authentication**: OAuth 2.0 and OpenID Connect integration
- **Regulatory Compliance**: Built-in support for GDPR, SOX, HIPAA, PCI-DSS

### 5. Interactive Execution Ledger
- **Live Recording**: Agents append entries via `execution_ledger.py` while executing — one event per write, timestamps assigned by the ledger, never batch-fabricated
- **Tamper Evidence**: SHA-256 hash chain over `ledger.jsonl` with end-to-end `verify`
- **Constraint Tracking**: Sessions declare `must_not`/`must` constraints; every close carries an upheld/violated report
- **Documentation**: See [EXECUTION_LEDGER.md](EXECUTION_LEDGER.md)

## 📋 Sample Configurations

### Agent Manifest Example
```yaml
apiVersion: v1
kind: Agent
metadata:
  name: data-processing-agent
  labels:
    environment: production
    type: data-processor
spec:
  agent:
    id: "agent-dp-001"
    name: "Data Processing Agent"
    type: "data-processor"
    version: "1.2.0"
  resources:
    cpu: "2"
    memory: "4Gi"
    storage: "10Gi"
  compliance:
    dataRetention: "90d"
    encryptionRequired: true
    auditLevel: "detailed"
```

### Receipt Example
```json
{
  "receipt": {
    "id": "tx-20241219-103045-001",
    "type": "operation",
    "timestamp": "2024-12-19T10:30:45.123Z"
  },
  "operation": {
    "id": "op-ml-training-20241219-001",
    "type": "ml-model-training",
    "status": "completed"
  },
  "agent": {
    "id": "agent-ml-001",
    "name": "ML Training Agent",
    "version": "2.1.0"
  },
  "signature": {
    "algorithm": "RSA-SHA256",
    "value": "MEQCIBc7...",
    "signed_by": "agent-ml-001"
  }
}
```

## 🔄 Workflow Examples

### Sequential Processing
```yaml
workflow:
  name: "data-processing-pipeline"
  pattern: "sequential"
  steps:
    - agent: "data-validation-agent"
      action: "validate-input"
    - agent: "data-transformation-agent"
      action: "transform-data"
    - agent: "ml-training-agent"
      action: "train-model"
```

### Parallel Analysis
```yaml
workflow:
  name: "parallel-analysis"
  pattern: "parallel"
  branches:
    - name: "risk-assessment"
      agent: "risk-assessment-agent"
    - name: "fraud-detection"
      agent: "fraud-detection-agent"
    - name: "compliance-check"
      agent: "compliance-agent"
```

## 📊 Compliance and Governance

### Data Retention Policies
| Data Type | Retention Period | Archive Policy | Compliance |
|-----------|------------------|----------------|------------|
| Audit Logs | 7 years | After 2 years | SOX, GDPR |
| Performance Logs | 1 year | After 3 months | Internal |
| Provenance Data | 5 years | After 1 year | All |
| Receipts | 10 years | After 3 years | Financial |

### Security Controls
- **Identity & Access Management**: OAuth 2.0, RBAC, ABAC
- **Network Security**: TLS 1.3, Zero Trust, Micro-segmentation
- **Data Protection**: AES-256 encryption, DLP, Data masking
- **Monitoring**: SIEM integration, Real-time alerting, Anomaly detection

## 🚦 Getting Started

### Prerequisites
- Python 3.9+ (standard library only for the ledger and tests)
- Optional: `ajv-cli` for JSON Schema validation, PyYAML for YAML checks

### Quick Start
```bash
# Clone the repository
git clone https://github.com/Donaldjohns0n/ai-agents-data-logs.git
cd ai-agents-data-logs

# Validate the repository (flat invariant, manifest, hashes, ledger chain, tests)
bash validate.sh

# Optional schema validation with ajv
npm install -g ajv-cli
ajv validate -s agent-manifest-schema.json -d agent-registry.json
ajv validate -s receipt-schema.json -d ml-training-receipt-20241219.json
```

### Configuration
1. Review `agent-config-template.yaml` for configuration examples
2. Customize agent configurations such as `ml-training-agent-config.json`
3. Deploy from the manifests `agent-registry.json` / `data-processing-agent.yaml`
4. Record live activity through `execution_ledger.py`; read it with `tail` / `query`
5. Trace any file's origin through `manifest.json`

## 📚 Documentation

- **[Contributing Guidelines](CONTRIBUTING.md)**: Data governance policies and contribution process
- **[Orchestration Framework](ORCHESTRATION_AND_COMPLIANCE.md)**: Technical documentation for cross-agent orchestration
- **[Execution Ledger](EXECUTION_LEDGER.md)**: Recording and verifying live agent activity
- **[Failure Doctrine](failure-doctrine.md)**: The rules this repository's layout and processes implement
- **Schema Documentation**: `agent-manifest-schema.json`, `receipt-schema.json`, `execution-ledger-entry-schema.json`

## 🔒 Security

- All sensitive data is encrypted at rest and in transit
- Access controls are enforced through RBAC policies
- Audit trails are maintained for all operations
- Regular security assessments are conducted

## 📞 Support

For questions, issues, or contributions:
- **Data Governance**: Review [CONTRIBUTING.md](CONTRIBUTING.md)
- **Technical Issues**: Start from this README's layout map and `manifest.json`
- **Security Concerns**: Follow incident response procedures
- **Compliance Questions**: Contact the compliance team

## 📄 License

This repository contains proprietary AI agent orchestration and compliance systems. All rights reserved.

---

*This repository serves as the central hub for AI agent data governance, ensuring transparency, compliance, and operational excellence in our multi-agent ecosystem.*
