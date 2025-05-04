"""
Tests for the logger.py module in hipaah/utils.
"""

import pytest
import os
import json
import tempfile
from io import StringIO
import sys
from unittest.mock import patch, mock_open, MagicMock
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
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_warning_method(self, mock_stdout):
        """Test the warning method."""
        logger = SafeLogger(["ssn"])
        
        data = {"name": "John Smith", "ssn": "123-45-6789"}
        message = "Access policy warning"
        
        logger.warning(message, data)
        
        output = mock_stdout.getvalue()
        
        # Verify output
        assert "[WARNING]" in output
        assert message in output
        assert "John Smith" in output
        assert "123-45-6789" not in output
        assert "***" in output
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_error_method(self, mock_stdout):
        """Test the error method."""
        logger = SafeLogger(["ssn"])
        
        data = {"name": "John Smith", "ssn": "123-45-6789"}
        message = "Policy evaluation error"
        
        logger.error(message, data)
        
        output = mock_stdout.getvalue()
        
        # Verify output
        assert "[ERROR]" in output
        assert message in output
        assert "John Smith" in output
        assert "123-45-6789" not in output
        assert "***" in output
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_justification_method(self, mock_stdout):
        """Test the justification method."""
        logger = SafeLogger()
        
        role = "billing_admin"
        intent = "billing"
        resource_id = "PAT12345"
        justification = "Monthly claims processing"
        
        # Call without expires_at
        logger.justification(role, intent, resource_id, justification)
        
        output = mock_stdout.getvalue()
        
        # Verify console output
        assert "Access justified by billing_admin for billing" in output
        assert "resource_id" in output
        assert "PAT12345" in output
        assert "has_expiry" in output
        assert "False" in output  # has_expiry should be False
        
        # Reset stdout for next test
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        # Call with expires_at
        expires_at = "2023-05-15T14:30:00.000Z"
        logger.justification(role, intent, resource_id, justification, expires_at)
        
        output = mock_stdout.getvalue()
        
        # Verify console output with expiry
        assert "Access justified by billing_admin for billing" in output
        assert "resource_id" in output
        assert "PAT12345" in output
        assert "has_expiry" in output
        assert "True" in output  # has_expiry should be True
        
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_justification_log_writing(self, mock_file, mock_makedirs):
        """Test writing justification to log file."""
        # Setup logger with file paths
        log_file_path = "/tmp/test/logs.jsonl"
        justification_log_path = "/tmp/test/justifications.jsonl"
        
        logger = SafeLogger(
            masked_fields=["ssn"],
            log_file_path=log_file_path,
            justification_log_path=justification_log_path
        )
        
        # Call justification method
        role = "billing_admin"
        intent = "billing"
        resource_id = "PAT12345"
        justification = "Monthly claims processing"
        expires_at = "2023-05-15T14:30:00.000Z"
        
        with patch('builtins.open', mock_open()) as m:
            logger.justification(role, intent, resource_id, justification, expires_at)
        
            # Verify directory creation
            mock_makedirs.assert_called_with(os.path.dirname(justification_log_path), exist_ok=True)
            
            # Verify file writing
            m.assert_any_call(justification_log_path, 'a')
            
            # Get the written data from all .write() calls
            write_calls = [call[0][0] for call in m().write.call_args_list]
            json_data = [json.loads(text) for text in write_calls if '{' in text]
            
            # Find the justification data in the JSON logs
            justification_data = None
            for data in json_data:
                if 'justification' in data:
                    justification_data = data
                    break
                    
            # Verify justification data was written
            assert justification_data is not None
            assert justification_data["role"] == role
            assert justification_data["intent"] == intent
            assert justification_data["resource_id"] == resource_id
            assert justification_data["justification"] == justification
            assert justification_data["expires_at"] == expires_at
            assert "timestamp" in justification_data
        
    def test_default_justification_log_path(self):
        """Test default justification log path generation."""
        log_file_path = "/tmp/logs/access.jsonl"
        
        # Create logger with only log file path
        logger = SafeLogger(log_file_path=log_file_path)
        
        # Verify default justification log path
        expected_path = "/tmp/logs/justification_log.jsonl"
        assert logger.justification_log_path == expected_path
        
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_log_file_writing(self, mock_file, mock_makedirs):
        """Test writing to log file."""
        log_file_path = "/tmp/test/logs.jsonl"
        
        logger = SafeLogger(
            masked_fields=["ssn"],
            log_file_path=log_file_path
        )
        
        # Log with sensitive data
        data = {
            "name": "John Smith",
            "ssn": "123-45-6789",
            "age": 42
        }
        
        message = "User data accessed"
        logger.info(message, data)
        
        # Verify directory creation
        mock_makedirs.assert_called_with(os.path.dirname(log_file_path), exist_ok=True)
        
        # Verify file writing
        mock_file.assert_called_with(log_file_path, 'a')
        
        # Get the written data
        write_call_args = mock_file().write.call_args[0][0]
        log_entry = json.loads(write_call_args)
        
        # Verify log entry
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == message
        assert log_entry["data"]["name"] == "John Smith"
        assert log_entry["data"]["ssn"] == "***"
        assert log_entry["data"]["age"] == 42
        assert "timestamp" in log_entry
        
    @patch('builtins.open')
    def test_file_write_error_handling(self, mock_open):
        """Test error handling when writing to log files fails."""
        # Setup mock to raise an exception
        mock_open.side_effect = IOError("Permission denied")
        
        log_file_path = "/tmp/test/logs.jsonl"
        logger = SafeLogger(log_file_path=log_file_path)
        
        # This should not raise an exception outside the logger
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.info("Test message", {"test": "data"})
            
            # Error message should be printed
            output = mock_stdout.getvalue()
            assert "Failed to write to log file" in output
            
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_log_file_directory_creation(self, mock_file, mock_makedirs):
        """Test directory creation for log files."""
        log_file_path = "/tmp/deep/nested/path/logs.jsonl"
        
        logger = SafeLogger(log_file_path=log_file_path)
        logger.info("Test message", {"test": "data"})
        
        # Verify directory creation
        mock_makedirs.assert_called_with("/tmp/deep/nested/path", exist_ok=True)
        
    def test_initialization_with_paths(self):
        """Test initialization with custom paths."""
        log_file_path = "/tmp/logs/access.jsonl"
        justification_log_path = "/tmp/logs/custom_justifications.jsonl"
        
        logger = SafeLogger(
            masked_fields=["ssn"], 
            log_file_path=log_file_path,
            justification_log_path=justification_log_path
        )
        
        assert logger.log_file_path == log_file_path
        assert logger.justification_log_path == justification_log_path