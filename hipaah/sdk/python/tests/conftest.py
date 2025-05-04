import os
import json
import pytest
import yaml
from pathlib import Path

# Sample policy for testing
SAMPLE_POLICY = """
- role: receptionist
  intent: treatment
  conditions:
    active_shift_only: true
  allow:
    - name
    - dob
    - appointment_time
  mask:
    - diagnosis
    - notes
  deny:
    - insurance_number

- role: nurse
  intent: treatment
  allow:
    - name
    - dob
    - diagnosis
    - medications
    - appointment_time
    - notes
  mask:
    - insurance_number

- role: doctor
  intent: treatment
  allow: "*"

- role: billing_admin
  intent: billing
  allow:
    - name
    - dob
    - insurance_number
    - billing_codes
  mask:
    - diagnosis
    - notes
  justification_ttl: 60
"""

# Sample resource for testing
SAMPLE_RESOURCE = {
    "name": "Lisa Chang",
    "dob": "1983-09-22",
    "diagnosis": "Asthma",
    "insurance_number": "123-45-6789",
    "appointment_time": "2025-05-10T09:30:00Z",
    "notes": "Patient reports shortness of breath during physical activity",
    "medications": ["Albuterol", "Fluticasone"],
    "billing_codes": ["J45.909", "Z79.51"]
}

@pytest.fixture
def policy_file(tmp_path):
    """Create a temporary policy file for testing."""
    policy_path = tmp_path / "test_policy.yaml"
    policy_path.write_text(SAMPLE_POLICY)
    return str(policy_path)

@pytest.fixture
def sample_resource():
    """Return a sample resource for testing."""
    return SAMPLE_RESOURCE.copy()

@pytest.fixture
def resource_file(tmp_path, sample_resource):
    """Create a temporary resource file for testing."""
    resource_path = tmp_path / "test_resource.json"
    with open(resource_path, "w") as f:
        json.dump(sample_resource, f)
    return str(resource_path)