# 🛡️ HIPAah Build Checklist & Directory Structure

## ✅ Master Feature List (MVP + Extended)

### Core Policy Engine
- [ ] Role-Based Access Control (RBAC)
- [ ] Attribute-Based Access Control (ABAC)
- [ ] Intent-based access scopes
- [ ] Field-level access policy evaluation
- [ ] Time-limited justifications
- [ ] Policy-as-code support (YAML/JSON)
- [ ] Policy versioning + rollback support

### SDKs + API
- [ ] FastAPI-based core server
- [ ] REST API for access decisions
- [ ] CLI tool (`hipaah`) to manage policies & test access
- [ ] Python SDK (`hipaah-py`)
- [ ] Node.js SDK (`hipaah-js`)
- [ ] Webhook support for access + policy events

### Log & Observability
- [ ] SafeLogger: redacting logger with field masking
- [ ] Auto-mask PHI from structured logs
- [ ] Log-level controls (`info`, `audit`, `restricted`)
- [ ] Role-based log viewer (e.g. for compliance vs devs)

### Audit + Compliance
- [ ] Immutable audit log of access decisions
- [ ] Justification logging & expiration logic
- [ ] API to export logs (CSV/JSON)
- [ ] Retention policy config

### LLM / AI Middleware
- [ ] Input masking layer (PHI tokenization)
- [ ] Output response scanner
- [ ] Proxy middleware for LLMs (e.g. OpenAI, Claude)
- [ ] Synthetic data generator for prompt testing
- [ ] Consent enforcement layer for model use

### Screenshot Mode
- [ ] Screenshot Mode toggle (env var + API flag)
- [ ] Synthetic PHI generator (name, dob, diagnosis, etc.)
- [ ] Safe UI annotation/watermarking
- [ ] Log sanitizer override
- [ ] Storybook/Figma export JSON

### FHIR Support (Stretch)
- [ ] Resource schema mappings (e.g. Patient, Observation)
- [ ] Field group mapping to FHIR standard
- [ ] FHIR policy evaluation engine

---

## 📁 Proposed Directory Structure

```plaintext
hipaah/
│
├── api/                        # FastAPI app
│   ├── main.py                # Entry point
│   ├── routes/                # All API endpoints
│   └── middleware/            # Justification, Screenshot Mode, etc.
│
├── core/                      # Business logic
│   ├── engine.py              # Policy evaluator
│   ├── policy_loader.py       # Loads YAML/JSON policies
│   ├── schema.py              # Field-level schema definitions
│   └── fhir_adapter.py        # FHIR field mapper (optional)
│
├── sdk/                       # SDKs
│   ├── python/hipaah/         # Python SDK
│   └── js/hipaah/             # JS SDK
│
├── utils/
│   ├── logger.py              # SafeLogger w/ masking
│   ├── mask.py                # Redaction + field masking
│   └── synthetic_data.py      # Faker-based screenshot data
│
├── cli/                       # CLI interface
│   └── cli.py                 # Policy testing, screenshot mode toggle, etc.
│
├── config/
│   ├── sample_policies/       # Starter YAML/JSON policies
│   └── schemas/               # Supported field models (e.g., patient_record.json)
│
├── data/                      # Logs, audit trails
│   ├── access_log.jsonl
│   └── justification_log.jsonl
│
├── tests/                     # Unit & integration tests
│
├── docs/                      # Markdown docs
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── architecture.md
│   └── compliance-model.md
│
├── .env.example               # Sample config for screenshot mode, etc.
├── pyproject.toml             # Poetry / pip project config
└── Dockerfile                 # Containerize it for easy deployment
```

---

## 🚀 Suggested Dev Stack

| Layer | Choice |
|-------|--------|
| Backend | Python + FastAPI |
| CLI | Typer |
| Data masking | Faker |
| Policy format | YAML + JSON |
| Dev tools | Poetry, pre-commit hooks, pytest |
| Docs | Markdown + MkDocs or Docusaurus (for hosted docs site) |
| Logging | JSON logs (loguru or stdlib) |
| Container | Docker |

---
