"""
Tests for the mask.py module in hipaah/utils.
"""

import pytest
import re
from hipaah.utils.mask import (
    mask_data,
    mask_phi_patterns,
    mask_fields_except,
    safe_log_filter,
    redact_json_for_logging,
    DEFAULT_MASK
)

class TestMaskData:
    """Tests for mask_data function."""
    
    def test_mask_basic_dict(self):
        """Test masking fields in a basic dictionary."""
        data = {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "ssn": "123-45-6789",
            "diagnosis": "Hypertension"
        }
        
        fields_to_mask = ["ssn", "diagnosis"]
        masked = mask_data(data, fields_to_mask)
        
        # Fields to mask should be masked
        assert masked["ssn"] == DEFAULT_MASK
        assert masked["diagnosis"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert masked["name"] == "John Smith"
        assert masked["email"] == "john.smith@example.com"
        
        # Original data should be unchanged
        assert data["ssn"] == "123-45-6789"
        assert data["diagnosis"] == "Hypertension"
        
    def test_mask_nested_dict(self):
        """Test masking fields in nested dictionaries."""
        data = {
            "name": "John Smith",
            "contact": {
                "email": "john.smith@example.com",
                "phone": "555-123-4567"
            },
            "medical": {
                "diagnosis": "Hypertension",
                "medications": ["Lisinopril", "Metoprolol"]
            }
        }
        
        fields_to_mask = ["phone", "diagnosis"]
        masked = mask_data(data, fields_to_mask)
        
        # Fields to mask should be masked at any level
        assert masked["contact"]["phone"] == DEFAULT_MASK
        assert masked["medical"]["diagnosis"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert masked["name"] == "John Smith"
        assert masked["contact"]["email"] == "john.smith@example.com"
        assert masked["medical"]["medications"] == ["Lisinopril", "Metoprolol"]
    
    def test_mask_list_of_dicts(self):
        """Test masking fields in a list of dictionaries."""
        data = [
            {"name": "John Smith", "ssn": "123-45-6789"},
            {"name": "Jane Doe", "ssn": "987-65-4321"}
        ]
        
        fields_to_mask = ["ssn"]
        masked = mask_data(data, fields_to_mask)
        
        # Fields to mask should be masked in each dict
        assert masked[0]["ssn"] == DEFAULT_MASK
        assert masked[1]["ssn"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert masked[0]["name"] == "John Smith"
        assert masked[1]["name"] == "Jane Doe"
    
    def test_mask_with_preserve_type(self):
        """Test masking with preserve_type option."""
        data = {
            "name": "John Smith",
            "age": 42,
            "active": True,
            "ssn": "123-45-6789"
        }
        
        fields_to_mask = ["name", "age", "active", "ssn"]
        masked = mask_data(data, fields_to_mask, preserve_type=True)
        
        # String fields should be masked with string mask
        assert masked["name"] == DEFAULT_MASK
        assert masked["ssn"] == DEFAULT_MASK
        
        # Numeric fields should be masked with 0
        assert masked["age"] == 0
        
        # Boolean fields should be masked with False
        assert masked["active"] is False
    
    def test_mask_with_edge_cases(self):
        """Test masking with edge cases."""
        # Test with empty fields to mask
        data = {"name": "John", "ssn": "123-45-6789"}
        assert mask_data(data, []) == data
        
        # Test with None data
        assert mask_data(None, ["anything"]) is None
        
        # Test with primitive types
        assert mask_data("John", ["anything"]) == "John"
        assert mask_data(42, ["anything"]) == 42
        assert mask_data(True, ["anything"]) is True

class TestMaskPhiPatterns:
    """Tests for mask_phi_patterns function."""
    
    def test_mask_ssn(self):
        """Test masking SSN patterns."""
        text = "Patient SSN is 123-45-6789 and should be kept confidential."
        masked = mask_phi_patterns(text)
        
        assert "123-45-6789" not in masked
        assert DEFAULT_MASK in masked
        
    def test_mask_phone(self):
        """Test masking phone number patterns."""
        text = "Call me at 555-123-4567 or (800) 555-1234."
        masked = mask_phi_patterns(text)
        
        assert "555-123-4567" not in masked
        assert "(800) 555-1234" not in masked
        assert DEFAULT_MASK in masked
        
    def test_mask_email(self):
        """Test masking email patterns."""
        text = "Contact me at john.smith@example.com."
        masked = mask_phi_patterns(text)
        
        assert "john.smith@example.com" not in masked
        assert DEFAULT_MASK in masked
        
    def test_mask_date(self):
        """Test masking date patterns."""
        text = "Date of birth: 01/15/1980 or 1980-01-15."
        masked = mask_phi_patterns(text)
        
        assert "01/15/1980" not in masked
        assert "1980-01-15" not in masked
        assert DEFAULT_MASK in masked
        
    def test_mask_custom_patterns(self):
        """Test masking with custom patterns."""
        text = "Patient ID: ABC-12345 and MRN: 987654."
        patterns = [r'ABC-\d+', r'MRN:\s*\d+']
        masked = mask_phi_patterns(text, patterns)
        
        assert "ABC-12345" not in masked
        assert "MRN: 987654" not in masked
        assert DEFAULT_MASK in masked
        
    def test_mask_with_compiled_regex(self):
        """Test masking with compiled regex patterns."""
        text = "Medical Record Number: MRN12345."
        pattern = re.compile(r'MRN\d+')
        masked = mask_phi_patterns(text, [pattern])
        
        assert "MRN12345" not in masked
        assert DEFAULT_MASK in masked
        
    def test_mask_with_edge_cases(self):
        """Test masking with edge cases."""
        # Test with empty text
        assert mask_phi_patterns("") == ""
        assert mask_phi_patterns(None) is None
        
        # Test with text containing no patterns
        text = "This text contains no PHI patterns."
        assert mask_phi_patterns(text) == text

class TestMaskFieldsExcept:
    """Tests for mask_fields_except function."""
    
    def test_mask_all_except_allowed(self):
        """Test masking all fields except those explicitly allowed."""
        data = {
            "name": "John Smith",
            "dob": "1980-01-15",
            "diagnosis": "Hypertension",
            "ssn": "123-45-6789",
            "notes": "Patient reports headaches."
        }
        
        allowed_fields = ["name", "dob"]
        masked = mask_fields_except(data, allowed_fields)
        
        # Allowed fields should be unchanged
        assert masked["name"] == "John Smith"
        assert masked["dob"] == "1980-01-15"
        
        # Other fields should be masked
        assert masked["diagnosis"] == DEFAULT_MASK
        assert masked["ssn"] == DEFAULT_MASK
        assert masked["notes"] == DEFAULT_MASK
        
    def test_mask_all_except_with_empty_allowed(self):
        """Test masking all fields with empty allowed list."""
        data = {
            "name": "John Smith",
            "ssn": "123-45-6789"
        }
        
        masked = mask_fields_except(data, [])
        
        # All fields should be masked
        assert masked["name"] == DEFAULT_MASK
        assert masked["ssn"] == DEFAULT_MASK
        
    def test_mask_fields_except_with_edge_cases(self):
        """Test masking except with edge cases."""
        # Test with non-dict input
        assert mask_fields_except("John", ["anything"]) == "John"
        assert mask_fields_except(42, ["anything"]) == 42
        assert mask_fields_except(None, ["anything"]) is None

class TestSafeLogFilter:
    """Tests for safe_log_filter function."""
    
    def test_safe_log_filter_with_user_fields(self):
        """Test safe log filter with user-provided fields."""
        log_data = {
            "name": "John Smith",
            "diagnosis": "Hypertension",
            "action": "view_record",
            "timestamp": "2023-01-01T12:00:00Z"
        }
        
        masked_fields = ["diagnosis"]
        filtered = safe_log_filter(log_data, masked_fields)
        
        # User-provided fields should be masked
        assert filtered["diagnosis"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert filtered["name"] == "John Smith"
        assert filtered["action"] == "view_record"
        assert filtered["timestamp"] == "2023-01-01T12:00:00Z"
        
    def test_safe_log_filter_with_default_sensitive_fields(self):
        """Test safe log filter with default sensitive fields."""
        log_data = {
            "name": "John Smith",
            "password": "secret123",  # Should be masked by default
            "ssn": "123-45-6789",  # Should be masked by default
            "action": "login"
        }
        
        filtered = safe_log_filter(log_data, [])
        
        # Default sensitive fields should be masked
        assert filtered["password"] == DEFAULT_MASK
        assert filtered["ssn"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert filtered["name"] == "John Smith"
        assert filtered["action"] == "login"
        
    def test_safe_log_filter_combined_fields(self):
        """Test safe log filter with both user and default fields."""
        log_data = {
            "name": "John Smith",
            "diagnosis": "Hypertension",  # User-specified
            "password": "secret123",  # Default sensitive
            "action": "view_record"
        }
        
        masked_fields = ["diagnosis"]
        filtered = safe_log_filter(log_data, masked_fields)
        
        # Both user-specified and default fields should be masked
        assert filtered["diagnosis"] == DEFAULT_MASK
        assert filtered["password"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert filtered["name"] == "John Smith"
        assert filtered["action"] == "view_record"

class TestRedactJsonForLogging:
    """Tests for redact_json_for_logging function."""
    
    def test_redact_phi_fields(self):
        """Test redacting PHI fields from data."""
        data = {
            "name": "John Smith",
            "diagnosis": "Hypertension",
            "medications": ["Lisinopril", "Metoprolol"]
        }
        
        phi_fields = ["diagnosis"]
        redacted = redact_json_for_logging(data, phi_fields)
        
        # PHI fields should be masked
        assert redacted["diagnosis"] == DEFAULT_MASK
        
        # Other fields should be unchanged
        assert redacted["name"] == "John Smith"
        assert redacted["medications"] == ["Lisinopril", "Metoprolol"]
        
    def test_redact_deep_structures(self):
        """Test redacting with deep nested structures."""
        data = {
            "name": "John Smith",
            "medical": {
                "conditions": {
                    "primary": {
                        "diagnosis": "Hypertension"
                    }
                }
            }
        }
        
        # Set max_depth to 2 (should truncate beyond medical.conditions)
        redacted = redact_json_for_logging(data, [], max_depth=2)
        
        # Nesting beyond max_depth should be truncated
        assert "... (truncated due to depth)" in str(redacted["medical"]["conditions"])
        
    def test_redact_large_arrays(self):
        """Test truncating large arrays."""
        data = {
            "name": "John Smith",
            "medications": ["Med1", "Med2", "Med3", "Med4", "Med5", "Med6"]
        }
        
        # Set max_array_items to 3
        redacted = redact_json_for_logging(data, [], max_array_items=3)
        
        # Array should be truncated to max_array_items + message
        assert len(redacted["medications"]) == 4  # 3 items + truncation message
        assert "Med1" in redacted["medications"]
        assert "Med2" in redacted["medications"]
        assert "Med3" in redacted["medications"]
        assert "... (3 more items)" in redacted["medications"]
        
    def test_redact_long_strings(self):
        """Test truncating long strings."""
        long_string = "a" * 200
        data = {
            "name": "John Smith",
            "notes": long_string
        }
        
        redacted = redact_json_for_logging(data, [])
        
        # Long string should be truncated
        assert len(redacted["notes"]) < 200
        assert "... (100 more chars)" in redacted["notes"]
        
    def test_redact_with_edge_cases(self):
        """Test redacting with edge cases."""
        # Test with empty data
        assert redact_json_for_logging({}, []) == {}