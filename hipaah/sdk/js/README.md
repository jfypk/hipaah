# HIPAAH JavaScript SDK

A JavaScript SDK for HIPAA-safe access control for healthtech developers.

## Installation

```bash
npm install hipaah
```

## Usage

### Basic Example

```javascript
const { HipaahClient, SafeLogger } = require('hipaah');

// Create a client instance with the policy file
const client = new HipaahClient('./policies/example_policy.yaml');

// Resource data (patient info)
const resource = {
  name: "Lisa Chang",
  dob: "1983-09-22",
  diagnosis: "Asthma",
  insurance_number: "123-45-6789"
};

// Policy evaluation parameters
const role = "receptionist";
const intent = "treatment";
const attributes = { active_shift_only: true };

// Evaluate the policy
const filtered = client.evaluate(resource, role, intent, attributes);

// Safely log the result, masking PHI fields
const logger = new SafeLogger(["diagnosis", "insurance_number"]);
logger.info("Filtered output for UI rendering", filtered);
```

### API Client Example

```javascript
const { ApiClient } = require('hipaah');

// Create API client
const client = new ApiClient(
  'https://api.example.com/hipaah',
  'your-api-key',
  './policies/fallback_policy.yaml'
);

// Use remote API for evaluation
async function evaluatePatientRecord() {
  const resource = {
    name: "John Doe",
    dob: "1975-05-15",
    diagnosis: "Hypertension",
    insurance_number: "987-65-4321"
  };
  
  try {
    const result = await client.remoteEvaluate(
      resource,
      "nurse",
      "billing",
      { department: "cardiology" }
    );
    
    console.log("Filtered result:", result);
  } catch (error) {
    console.error("API evaluation failed:", error);
  }
}

evaluatePatientRecord();
```

### Batch Processing

```javascript
const { HipaahClient, loadResourceFromFile, saveResourceToFile } = require('hipaah');

// Load multiple patient records
const patients = loadResourceFromFile('./data/patients.json');

// Create client and evaluate all records
const client = new HipaahClient('./policies/example_policy.yaml');
const filteredResults = client.batchEvaluate(
  patients,
  "receptionist",
  "scheduling"
);

// Save filtered results
saveResourceToFile(filteredResults, './data/filtered_patients.json');
```

## API Reference

### Classes

#### HipaahClient

Main client for policy evaluation.

- `constructor(policyPath)`: Create client, optionally loading a policy file
- `loadPolicy(policyPath)`: Load policies from a YAML file
- `evaluate(resource, role, intent, attributes)`: Evaluate a resource against policies
- `batchEvaluate(resources, role, intent, attributes)`: Evaluate multiple resources

#### ApiClient

Client for interacting with the HIPAAH API.

- `constructor(apiUrl, apiKey, policyPath)`: Create API client
- `remoteEvaluate(resource, role, intent, attributes)`: Evaluate using remote API

#### SafeLogger

Logger that safely masks sensitive fields.

- `constructor(maskedFields)`: Create logger with fields to mask
- `info(message, data)`: Log info message
- `warning(message, data)`: Log warning message
- `error(message, data)`: Log error message

### Utility Functions

- `loadResourceFromFile(filePath)`: Load resource from JSON file
- `saveResourceToFile(resource, filePath)`: Save resource to JSON file
- `maskPhiFields(data, fieldsToMask)`: Mask sensitive fields in data
- `mergePolicies(policyFiles)`: Merge multiple policy files