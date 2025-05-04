# 🛡️ HIPAah Build Checklist & Directory Structure

## ✅ Master Feature List (MVP + Extended)

### Core Policy Engine
- [x] Role-Based Access Control (RBAC)
- [x] Attribute-Based Access Control (ABAC)
- [x] Intent-based access scopes
- [x] Field-level access policy evaluation
- [x] Time-limited justifications
- [x] Policy-as-code support (YAML/JSON)
- [ ] Policy versioning + rollback support

### SDKs + API
- [ ] FastAPI-based core server
- [ ] REST API for access decisions
- [x] CLI tool (`hipaah`) to manage policies & test access
- [x] Python SDK (`hipaah-py`)
- [x] Node.js SDK (`hipaah-js`)
- [ ] Webhook support for access + policy events

### Log & Observability
- [x] SafeLogger: redacting logger with field masking
- [x] Auto-mask PHI from structured logs
- [x] Log-level controls (`info`, `audit`, `restricted`)
- [ ] Role-based log viewer (e.g. for compliance vs devs)

### Audit + Compliance
- [x] Immutable audit log of access decisions
- [x] Justification logging & expiration logic
- [ ] API to export logs (CSV/JSON)
- [ ] Retention policy config

### LLM / AI Middleware
- [x] Input masking layer (PHI tokenization)
- [ ] Output response scanner
- [ ] Proxy middleware for LLMs (e.g. OpenAI, Claude)
- [x] Synthetic data generator for prompt testing
- [ ] Consent enforcement layer for model use

### Screenshot Mode
- [ ] Screenshot Mode toggle (env var + API flag)
- [x] Synthetic PHI generator (name, dob, diagnosis, etc.)
- [x] Safe UI annotation/watermarking
- [x] Log sanitizer override
- [ ] Storybook/Figma export JSON

### FHIR Support (Stretch)
- [ ] Resource schema mappings (e.g. Patient, Observation)
- [ ] Field group mapping to FHIR standard
- [ ] FHIR policy evaluation engine

---

## 📁 Current Directory Structure

```plaintext
.
├── config
│   ├── sample_policies      # Sample policy files
│   │   └── example_policy.yaml
│   └── schemas             # JSON schemas for data structures
│       └── patient_record.json
├── CONTRIBUTING.md
├── data                    # Audit logs
│   ├── access_log.jsonl
│   └── justification_log.jsonl
├── Dockerfile              # Containerize it for easy deployment
├── hipaah
│   ├── __init__.py
│   ├── api                 # FastAPI server
│   │   ├── main.py
│   │   ├── middleware
│   │   └── routes
│   ├── cli                 # Command line tool 
│   │   └── cli.py
│   ├── core                # Policy engine & evaluators
│   │   ├── engine.py
│   │   ├── policy_loader.py
│   │   └── types.py
│   ├── sdk                 # Python + JS SDKs
│   │   ├── js             # JavaScript SDK
│   │   └── python         # Python SDK
│   └── utils               # Log masking, fake data, etc.
│       ├── logger.py       # SafeLogger w/ masking
│       ├── mask.py         # Redaction + field masking
│       └── synthetic_data.py # Faker-based screenshot data
├── LICENSE
├── poetry.lock
├── pyproject.toml          # Poetry / pip project config
├── README.md
├── TAXONOMY.md
├── tests                   # Unit & integration tests
│   ├── conftest.py
│   ├── core
│   │   └── test_engine.py
│   └── utils
│       ├── test_logger.py
│       ├── test_mask.py
│       └── test_synthetic_data.py
└── todo.md
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
