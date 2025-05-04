"""
Tests for the logger.py module in hipaah/utils.
"""

import pytest
from io import StringIO
import sys
from unittest.mock import patch
from hipaah.utils.logger import SafeLogger

class TestSafeLogger:
    """Test suite for the SafeLogger class."""
    
    def test_initialization(self):
        """Test basic initialization of the SafeLogger."""
        # Default initialization should have empty masked fields
        logger = SafeLogger()
        assert logger.masked_fields == set()
        
        # Initialization with masked fields
        masked_fields = ["ssn", "diagnosis", "insurance_number"]
        logger = SafeLogger(masked_fields)
        assert logger.masked_fields == set(masked_fields)
        
        # Initialization with None should result in empty set
        logger = SafeLogger(None)
        assert logger.masked_fields == set()
    
    def test_redact_method(self):
        """Test the redact method that masks sensitive fields."""
        masked_fields = ["ssn", "diagnosis"]
        logger = SafeLogger(masked_fields)
        
        # Test with data containing masked fields
        data = {
            "name": "John Smith",
            "age": 42,
            "ssn": "123-45-6789",
            "diagnosis": "Hypertension",
            "notes": "Regular checkup"
        }
        
        redacted = logger.redact(data)
        
        # Masked fields should be replaced with '***'
        assert redacted["ssn"] == "***"
        assert redacted["diagnosis"] == "***"
        
        # Non-masked fields should remain unchanged
        assert redacted["name"] == "John Smith"
        assert redacted["age"] == 42
        assert redacted["notes"] == "Regular checkup"
        
        # Original data should be unchanged
        assert data["ssn"] == "123-45-6789"
        assert data["diagnosis"] == "Hypertension"
    
    def test_redact_with_empty_masked_fields(self):
        """Test redacting with no masked fields."""
        logger = SafeLogger()
        
        data = {
            "name": "John Smith",
            "ssn": "123-45-6789"
        }
        
        redacted = logger.redact(data)
        
        # No fields should be masked
        assert redacted["name"] == "John Smith"
        assert redacted["ssn"] == "123-45-6789"
    
    def test_redact_with_missing_fields(self):
        """Test redacting when masked fields don't exist in data."""
        masked_fields = ["ssn", "diagnosis"]
        logger = SafeLogger(masked_fields)
        
        # Data doesn't contain any of the masked fields
        data = {
            "name": "John Smith",
            "age": 42
        }
        
        redacted = logger.redact(data)
        
        # Should handle missing fields gracefully
        assert redacted["name"] == "John Smith"
        assert redacted["age"] == 42
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_info_method(self, mock_stdout):
        """Test the info method that logs messages with redacted data."""
        masked_fields = ["ssn", "diagnosis"]
        logger = SafeLogger(masked_fields)
        
        # Test logging with sensitive data
        data = {
            "name": "John Smith",
            "ssn": "123-45-6789",
            "diagnosis": "Hypertension"
        }
        
        message = "Patient record accessed"
        logger.info(message, data)
        
        # Check output format and content
        output = mock_stdout.getvalue()
        
        # Output should contain the message
        assert message in output
        
        # Output should contain [INFO] prefix
        assert "[INFO]" in output
        
        # Output should contain masked fields
        assert "***" in output
        
        # Output should contain non-masked fields
        assert "John Smith" in output
        
        # Sensitive data should not appear in the output
        assert "123-45-6789" not in output
        assert "Hypertension" not in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_info_with_empty_data(self, mock_stdout):
        """Test info method with empty data."""
        logger = SafeLogger(["any_field"])
        
        # Empty data
        logger.info("Empty data test", {})
        
        output = mock_stdout.getvalue()
        
        # Should handle empty data gracefully
        assert "[INFO] Empty data test {}" in output