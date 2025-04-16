# 📘 HIPAah Terminology Glossary

A shared language for discussing, documenting, and developing HIPAah integrations.

---

## 📦 Core Entities

| Term | Definition |
|------|------------|
| **HIPAah** | The open-source authorization engine and policy server that enforces field-level access, built to support HIPAA compliance. |
| **HIPAah App** | The deployed instance of HIPAah, either self-hosted or SaaS, providing APIs, SDKs, CLI, and logging. |
| **Application** | A product (e.g. EHR, care platform, LLM assistant) that integrates with HIPAah to control access to health data. |
| **Client** | A user interface or API consumer of the Application (e.g. web frontend, mobile app, third-party API user). |
| **Application Devs** | Engineers building and maintaining the Application that uses HIPAah (your primary target users). |
| **Roles** | Logical representations of real-world actors (e.g., `doctor`, `nurse`, `admin`, `patient`) defined in the Application and used by HIPAah to evaluate access policies. |

---

## ⚙️ System Concepts

| Term | Definition |
|------|------------|
| **Policy** | A declarative set of rules written in YAML or JSON, stored in the HIPAah App, that defines which Roles can access which fields under what conditions. |
| **Access Decision** | The result of evaluating a request against HIPAah's policies — returns `allow`, `mask`, or `deny` fields. |
| **Justification** | A user-provided reason required to access sensitive data fields, especially when elevated access is granted. |
| **Intent** | The declared purpose of a request (e.g. `treatment`, `billing`, `research`), used to scope access. |
| **Attributes** | Runtime context passed by the Application to HIPAah (e.g., `department`, `location`, `active_shift_only`) used in policy evaluation. |
| **Field-Level Access** | The ability to allow or deny visibility to individual fields in a resource (e.g., `diagnosis`, `insurance_number`). |
| **Masking** | The act of redacting or replacing a field with a placeholder (e.g., `***`) in the output returned by the Application to the Client. |
| **Screenshot Mode** | A special mode where HIPAah returns synthetic, fake PHI (e.g., “Lisa Chang, Asthma”) for safe use in UI testing, demos, and marketing. |
| **Audit Trail** | A tamper-resistant log of all access decisions, justifications, and policy evaluations — exportable for compliance. |
| **PHI (Protected Health Information)** | Health-related data governed by HIPAA that must be protected, and never passed to HIPAah itself. |

---

## 🧠 Advanced Distinctions

| Term | Definition |
|------|------------|
| **PEP (Policy Enforcement Point)** | The part of the Application (often backend or middleware) that enforces the access decisions returned by HIPAah. |
| **PDP (Policy Decision Point)** | HIPAah itself — it evaluates the policy and returns what should be allowed, masked, or denied. |
| **Session Context** | Runtime metadata from the Application that HIPAah uses to evaluate access rules (e.g., logged-in role, location, active shift). |
| **Scope** | A subset of data or actions associated with a specific purpose (e.g., `can_read:diagnosis` when intent = `treatment`). |
| **Consumer Organization** | The business entity or team using the HIPAah App in their Application (e.g., a startup, a clinic, a healthtech company). |
