# HIPAAH Python SDK

A Python SDK for HIPAA-safe access control for healthtech developers.

## Installation

```bash
pip install hipaah
```

## Usage

```python
from hipaah import HipaahClient, SafeLogger

# Create a client instance with the policy file
client = HipaahClient("path/to/policy.yaml")

# Resource data (patient info)
resource = {
    "name": "Lisa Chang",
    "dob": "1983-09-22",
    "diagnosis": "Asthma",
    "insurance_number": "123-45-6789"
}

# Policy evaluation parameters
role = "receptionist"
intent = "treatment"
attributes = {"active_shift_only": True}

# Evaluate the policy
filtered = client.evaluate(resource, role, intent, attributes)

# Safely log the result, masking PHI fields
logger = SafeLogger(masked_fields=["diagnosis", "insurance_number"])
logger.info("Filtered output for UI rendering", filtered)
```

## API Reference

### HipaahClient

The main client class for interacting with the HIPAAH SDK.

#### Methods

- `__init__(policy_path=None)`: Initialize the client with an optional policy file
- `load_policy(policy_path)`: Load policies from a file
- `evaluate(resource, role, intent, attributes=None)`: Evaluate a resource against loaded policies

### SafeLogger

A logger that safely masks sensitive fields in logs.

#### Methods

- `__init__(masked_fields=None)`: Initialize with a list of fields to mask
- `info(message, data=None)`: Log an info message with optional data
- `warning(message, data=None)`: Log a warning message with optional data
- `error(message, data=None)`: Log an error message with optional data