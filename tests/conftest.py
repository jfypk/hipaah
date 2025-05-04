"""
Shared fixtures for HIPAah tests.
"""

import pytest
import os
import tempfile
import json

@pytest.fixture
def sample_phi_data():
    """Sample PHI data for testing masking functions."""
    return {
        "name": "John Smith",
        "dob": "1980-01-15",
        "ssn": "123-45-6789",
        "diagnosis": "Hypertension",
        "insurance_number": "ABC123456789",
        "phone": "555-123-4567",
        "email": "john.smith@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        },
        "notes": "Patient reports occasional headaches.",
        "medications": [
            "Lisinopril 10mg",
            "Metoprolol 25mg"
        ],
        "lab_results": [
            {
                "date": "2023-01-15",
                "test": "Blood Pressure",
                "result": "140/90"
            },
            {
                "date": "2023-01-15",
                "test": "Cholesterol",
                "result": "200 mg/dL"
            }
        ]
    }

@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_data_file(temp_dir, sample_phi_data):
    """Create a temporary file with sample data."""
    file_path = os.path.join(temp_dir, "sample_data.json")
    with open(file_path, 'w') as f:
        json.dump(sample_phi_data, f)
    return file_path