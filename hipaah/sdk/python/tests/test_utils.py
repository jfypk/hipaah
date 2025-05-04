import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from hipaah import (
    load_resource_from_file,
    save_resource_to_file,
    mask_phi_fields,
    merge_policies
)

class TestUtilityFunctions:
    
    def test_load_resource_from_file(self, resource_file, sample_resource):
        """Test loading resources from a file."""
        # Test with valid file
        loaded = load_resource_from_file(resource_file)
        assert loaded == sample_resource
        
        # Test with invalid file
        with pytest.raises(Exception):
            load_resource_from_file("nonexistent_file.json")
    
    def test_save_resource_to_file(self, tmp_path, sample_resource):
        """Test saving resources to a file."""
        # Create a file path
        file_path = tmp_path / "output_resource.json"
        
        # Save the resource
        save_resource_to_file(sample_resource, str(file_path))
        
        # Verify file exists
        assert file_path.exists()
        
        # Verify contents
        with open(file_path, "r") as f:
            loaded = json.load(f)
            assert loaded == sample_resource
    
    def test_mask_phi_fields(self):
        """Test masking PHI fields in data."""
        data = {
            "name": "John Smith",
            "diagnosis": "Hypertension",
            "insurance_number": "123-45-6789",
            "notes": "Patient reported headaches"
        }
        
        # Test masking specific fields
        fields_to_mask = ["diagnosis", "insurance_number"]
        masked = mask_phi_fields(data, fields_to_mask)
        
        # Masked fields should be replaced
        assert masked["diagnosis"] == "***"
        assert masked["insurance_number"] == "***"
        
        # Non-masked fields should remain unchanged
        assert masked["name"] == data["name"]
        assert masked["notes"] == data["notes"]
        
        # Original data should be unchanged
        assert data["diagnosis"] == "Hypertension"
        assert data["insurance_number"] == "123-45-6789"
    
    def test_mask_phi_fields_nested(self):
        """Test masking PHI fields in nested data structures."""
        data = {
            "name": "John Smith",
            "medical": {
                "diagnosis": "Hypertension",
                "insurance_number": "123-45-6789"
            },
            "visits": [
                {"date": "2023-01-01", "diagnosis": "Headache"},
                {"date": "2023-02-01", "diagnosis": "Follow-up"}
            ]
        }
        
        # Test masking in nested structures
        fields_to_mask = ["diagnosis", "insurance_number"]
        masked = mask_phi_fields(data, fields_to_mask)
        
        # Check nested object
        assert masked["medical"]["diagnosis"] == "***"
        assert masked["medical"]["insurance_number"] == "***"
        
        # Check nested array
        assert masked["visits"][0]["diagnosis"] == "***"
        assert masked["visits"][1]["diagnosis"] == "***"
    
    def test_mask_phi_fields_edge_cases(self):
        """Test masking PHI fields with edge cases."""
        # Test with empty data
        assert mask_phi_fields({}, ["anything"]) == {}
        
        # Test with no fields to mask
        data = {"name": "John", "age": 30}
        assert mask_phi_fields(data, []) == data
        
        # Test with non-dict input
        assert mask_phi_fields("just a string", ["anything"]) == "just a string"
        assert mask_phi_fields(42, ["anything"]) == 42
        assert mask_phi_fields(None, ["anything"]) is None
    
    def test_merge_policies(self, policy_file, tmp_path):
        """Test merging multiple policy files."""
        # Create a second policy file
        second_policy = """
        - role: researcher
          intent: analytics
          allow:
            - diagnosis
            - medications
          mask:
            - name
            - dob
          deny:
            - insurance_number
        """
        second_file = tmp_path / "second_policy.yaml"
        second_file.write_text(second_policy)
        
        # Merge policies
        merged = merge_policies([policy_file, str(second_file)])
        
        # Result should be an array
        assert isinstance(merged, list)
        
        # Should contain all policies
        roles = [p.get("role") for p in merged]
        assert "receptionist" in roles
        assert "doctor" in roles
        assert "researcher" in roles
        
        # Should preserve policy details
        researcher_policy = next(p for p in merged if p.get("role") == "researcher")
        assert researcher_policy.get("intent") == "analytics"
        assert "diagnosis" in researcher_policy.get("allow", [])
        
    def test_merge_policies_error(self):
        """Test merge_policies with invalid input."""
        with pytest.raises(Exception):
            merge_policies(["nonexistent_file.yaml"])