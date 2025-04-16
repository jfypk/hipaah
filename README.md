# 🛡️ HIPAah

**HIPAah** is an open-source, developer-first **authorization engine for HIPAA-compliant apps**.

It gives you fine-grained control over who can access which health data fields, for what purpose, and for how long — without ever touching actual PHI.

---

## 🚀 Why HIPAah?

If you're building in healthtech, you're either:

- Manually coding access control logic 😩
- Exposing PHI in logs 😱
- Or delaying product launches over HIPAA compliance 🧯

HIPAah solves all of that by giving you:

- ✅ **RBAC + ABAC** policy enforcement
- ✅ **Field-level access masking**
- ✅ **Intent-based scopes** (treatment, billing, research, etc.)
- ✅ **Time-limited justifications**
- ✅ **Safe logging and audit trails**
- ✅ **Screenshot Mode** with synthetic PHI
- ✅ **LLM prompt masking and proxying**
- ✅ All while **never touching actual PHI**

---

## 🧠 Example Use Case

A nurse requests a patient record. The app calls HIPAah:

```json
{
  "role": "nurse",
  "intent": "treatment",
  "requested_fields": ["name", "dob", "diagnosis", "insurance_number"],
  "attributes": { "department": "oncology" },
  "justification": "Assisting attending physician"
}
```

HIPAah responds:

```json
{
  "allow": ["name", "dob"],
  "mask": ["diagnosis", "insurance_number"],
  "expires_at": "2025-04-15T12:30:00Z"
}
```

The frontend masks restricted fields and logs the access — safely, with zero PHI exposure.

---

## 🧩 Core Features

### 🔐 Access Control
- [] Role-Based Access Control (RBAC)
- [] Attribute-Based Access Control (ABAC)
- [] Intent-based access scopes
- [] Time-limited justifications

### 🧱 Developer Tools
- [] YAML/JSON policy files
- [] FastAPI-based PDP API
- [] Python + JS SDKs
- [] CLI to test and manage policies

### 📜 Audit + Logs
- [] Redacting logger
- [] Immutable audit log
- [] Role-based log viewer (WIP)

### 🤖 AI + LLM Integration
- [] PHI masking for prompts
- [] Response scrubber
- [] OpenAI proxy (WIP)

### 🖼️ Screenshot Mode
- [] Toggle for fake-PHI display
- [] Synthetic data generation (Faker-based)
- [] Visual watermarking

---

## 📦 Installation (Dev Mode)

```bash
git clone https://github.com/YOUR_USERNAME/hipaah.git
cd hipaah
poetry install
cp .env.example .env
uvicorn api.main:app --reload
```

To try the CLI:

```bash
poetry run hipaah --help
```

---

## 🛠️ Project Layout

```plaintext
hipaah/
├── api/              # FastAPI server
├── core/             # Policy engine & evaluators
├── sdk/              # Python + JS SDKs
├── cli/              # Command line tool
├── utils/            # Log masking, fake data, etc.
├── config/           # Sample policies & schemas
├── data/             # Audit logs
└── docs/             # Documentation
```

---

## 💬 Community + Contributing

We’re just getting started and **we’d love your help**.

- Star ⭐ the repo
- File issues / feature requests
- PRs welcome! See [`CONTRIBUTING.md`](docs/CONTRIBUTING.md)

---

## 📜 License

[MIT License](LICENSE)

---

## ❤️ Built for...

- Healthtech hackers
- Devs building HIPAA MVPs
- Agencies shipping for hospitals
- LLM prompt engineers who want to stay compliant
- You?

---
**HIPAA? Ahh. We've got you.**
