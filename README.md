# HIPAah

**HIPAah** is an open-source, developer-first **authorization engine for HIPAA-compliant apps**.

It gives you fine-grained control over who can access which health data fields, for what purpose, and for how long — without ever touching actual PHI.

---

## Why HIPAah?

If you're building in healthtech, you're either:

- Manually coding access control logic 
- Exposing PHI in logs 
- Or delaying product launches over HIPAA compliance 

HIPAah solves all of that by giving you:

-  **RBAC + ABAC** policy enforcement
-  **Field-level access masking**
-  **Intent-based scopes** (treatment, billing, research, etc.)
-  **Time-limited justifications**
-  **Safe logging and audit trails**
-  **Screenshot Mode** with synthetic PHI
-  **LLM prompt masking and proxying**
-  All while **never touching actual PHI**

---

## Example Use Case

Your application has a billing admin who needs temporary access to a patient's insurance information:

```javascript
// Patient record with sensitive PHI
const patientRecord = {
  id: "P12345",
  name: "Lisa Chang",
  dob: "1983-09-22",
  diagnosis: "Asthma",
  medications: ["Albuterol", "Fluticasone"],
  insurance_number: "123-45-6789",
  notes: "Patient reports increased shortness of breath"
};

// Create a HIPAah client with your policies
const { HipaahClient, SafeLogger } = require('hipaah');
const client = new HipaahClient('config/sample_policies/example_policy.yaml');
const logger = new SafeLogger(["diagnosis", "insurance_number", "notes"]);

// Request access with time-limited justification
const filteredRecord = client.evaluate(
  patientRecord,
  "billing_admin",
  "billing",
  { justification: "Monthly insurance claim processing" }
);

console.log(filteredRecord);
// Output:
// {
//   name: "Lisa Chang",
//   dob: "1983-09-22",
//   insurance_number: "123-45-6789",
//   billing_codes: ["J45.909", "Z79.51"],
//   diagnosis: "***",
//   notes: "***",
//   _meta: {
//     expires_at: "2023-05-15T15:30:00.000Z"  // Access expires in 60 minutes
//   }
// }

// Safely log the access with justification
logger.justification(
  "billing_admin", 
  "billing", 
  "P12345", 
  "Monthly insurance claim processing",
  filteredRecord._meta.expires_at
);
```

The same functionality is available in the Python SDK:

```python
from hipaah import HipaahClient, SafeLogger

# Create client and logger
client = HipaahClient("config/sample_policies/example_policy.yaml")
logger = SafeLogger(masked_fields=["diagnosis", "insurance_number"])

# Evaluate with justification
billing_view = client.evaluate(
    resource=patient_record,
    role="billing_admin",
    intent="billing",
    attributes={"justification": "Monthly insurance claim processing"}
)

# Access expires after the time specified in the policy
expires_at = billing_view.get("_meta", {}).get("expires_at")
print(f"Access granted until: {expires_at}")

# Log the justification
logger.justification(
    role="billing_admin",
    intent="billing",
    resource_id=patient_record["id"],
    justification="Monthly insurance claim processing",
    expires_at=expires_at
)
```

HIPAah enforces proper access control while maintaining an audit trail of all justified access to sensitive PHI.

---

## Core Features

### Access Control
- [x] Role-Based Access Control (RBAC)
- [x] Attribute-Based Access Control (ABAC)
- [x] Intent-based access scopes
- [x] Time-limited justifications

### Developer Tools
- [x] YAML/JSON policy files
- [ ] FastAPI-based PDP API (in progress)
- [x] Python + JS SDKs
- [ ] CLI to test and manage policies (in progress)

### Audit + Logs
- [x] Redacting logger
- [x] Immutable audit log
- [ ] Role-based log viewer (planned)

### AI + LLM Integration
- [x] PHI masking for prompts
- [x] Response scrubber
- [ ] OpenAI proxy (planned)

### Screenshot Mode
- [x] Toggle for fake-PHI display
- [x] Synthetic data generation (using built-in generator)
- [x] Visual watermarking

---

## Installation (Dev Mode)

```bash
git clone https://github.com/YOUR_USERNAME/hipaah.git
cd hipaah
poetry install
cp env.example .env
```

### Using the CLI

Test policies against sample data:

```bash
# Test a doctor accessing treatment data
poetry run hipaah \
  --role doctor \
  --intent treatment \
  config/sample_policies/example_policy.yaml \
  config/schemas/sample_patient.json

# [INFO] Access decision {'name': 'Lisa Chang', 'dob': '1983-09-22', 'diagnosis': 'Asthma', 'medications': ['Albuterol', 'Fluticasone'], 'insurance_number': '123-45-6789', 'appointment_time': '2023-05-15T10:30:00Z', 'notes': 'Patient reports increased shortness of breath'}

# Test a nurse assessing treatment data
poetry run hipaah \
  --role nurse \
  --intent treatment \
  config/sample_policies/example_policy.yaml \
  config/schemas/sample_patient.json

# [INFO] Access decision {'name': 'Lisa Chang', 'dob': '1983-09-22', 'diagnosis': 'Asthma', 'medications': ['Albuterol', 'Fluticasone'], 'insurance_number': '***', 'appointment_time': '2023-05-15T10:30:00Z', 'notes': 'Patient reports increased shortness of breath'}

# Test a nurse assessing treatment data
poetry run hipaah \
  --role billing_admin \
  --intent treatment \
  config/sample_policies/example_policy.yaml \
  config/schemas/sample_patient.json

# [INFO] Access decision {}

# View help
poetry run hipaah --help
```

### Using the JavaScript SDK

```javascript
const { HipaahClient, SafeLogger, maskPhiFields, generateSyntheticData } = require('hipaah');

// Create a client instance with the policy file
const client = new HipaahClient('path/to/policy.yaml');

// 1. Policy evaluation
const filteredData = client.evaluate(
  patientData,
  "nurse",
  "treatment",
  { department: "oncology" }
);

// 2. Safe logging
const logger = new SafeLogger(["diagnosis", "insurance_number"]);
logger.info("Filtered patient data", filteredData);

// 3. Batch processing
const batchResults = client.batchEvaluate(patientRecords, "billing_admin", "billing", {});

// 4. Mask specific PHI fields in any data structure
const maskedData = maskPhiFields(patientData, ["diagnosis", "insurance_number"]);

// 5. Generate synthetic data for screenshots/demos
const syntheticPatient = generateSyntheticData({
  name: "",
  dob: "",
  diagnosis: "",
  insurance_number: ""
}, true); // true adds watermark
```

### Using the Python SDK

```python
from hipaah import HipaahClient, SafeLogger
from hipaah.utils.mask import mask_data, mask_phi_patterns
from hipaah.utils.synthetic_data import generate_demo_patient

# 1. Create a client with policy
client = HipaahClient(policy_path="path/to/policy.yaml")

# 2. Evaluate access
result = client.evaluate(
    resource=patient_data,
    role="doctor",
    intent="treatment",
    attributes={"department": "cardiology"}
)

# 3. Safe logging
logger = SafeLogger(masked_fields=["diagnosis", "insurance_number"])
logger.info("Access granted", {"user_role": "doctor", "resource_id": patient_id})

# 4. Mask PHI in text
redacted_notes = mask_phi_patterns(patient_notes)

# 5. Generate synthetic data for screenshots
synthetic_patient = generate_demo_patient()
```

---

## Project Layout

```plaintext
.
├── config
│   ├── sample_policies      # Sample policy files
│   │   └── example_policy.yaml
│   └── schemas             # JSON schemas for data structures
│       └── patient_record.json
├── data                    # Audit logs
│   ├── access_log.jsonl
│   └── justification_log.jsonl
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
│   │   ├── js
│   │   └── python
│   └── utils               # Log masking, fake data, etc.
│       ├── logger.py
│       ├── mask.py
│       └── synthetic_data.py
└── tests                   # Unit & integration tests
    ├── core
    │   └── test_engine.py
    └── utils
        ├── test_logger.py
        ├── test_mask.py
        └── test_synthetic_data.py
```

---

## Community + Contributing

We're just getting started and **we'd love your help**.

- Star ⭐ the repo
- File issues / feature requests
- PRs welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md)

---

## License

This project is dual-licensed under [MPL 2.0](LICENSE) for open source use and a commercial license for proprietary use.

- **Open Source**: Use under MPL 2.0 terms
- **Commercial**: Contact aventyrlabs@gmail.com for commercial licensing options

---

## Built for...

- Healthtech hackers
- Devs building HIPAA MVPs
- Agencies shipping for hospitals
- LLM prompt engineers who want to stay compliant
- You?

---
**HIPAA? Ahh. We've got you.**