"""
Tests for the synthetic_data.py module in hipaah/utils.
"""

import os
import re
import json
import pytest
import datetime
from unittest.mock import patch, mock_open
from hipaah.utils.synthetic_data import (
    SyntheticDataGenerator,
    generate_demo_patient,
    generate_sample_dataset,
    transform_real_to_synthetic,
    FIRST_NAMES,
    LAST_NAMES,
    MEDICAL_CONDITIONS,
    MEDICATIONS
)

class TestSyntheticDataGenerator:
    """Tests for the SyntheticDataGenerator class."""
    
    def test_initialization(self):
        """Test basic initialization."""
        generator = SyntheticDataGenerator()
        assert generator is not None
        
        # Test with seed
        generator_with_seed = SyntheticDataGenerator(seed=42)
        assert generator_with_seed is not None
    
    def test_generate_name(self):
        """Test name generation."""
        generator = SyntheticDataGenerator(seed=42)
        name = generator.generate_name()
        
        # Name should be a string
        assert isinstance(name, str)
        
        # Name should have format "First Last"
        assert " " in name
        first, last = name.split(" ", 1)
        assert first in FIRST_NAMES
        assert last in LAST_NAMES
        
        # With fixed seed, should get reproducible results
        generator2 = SyntheticDataGenerator(seed=42)
        name2 = generator2.generate_name()
        assert name == name2
    
    def test_generate_dob(self):
        """Test date of birth generation."""
        generator = SyntheticDataGenerator()
        dob = generator.generate_dob()
        
        # DOB should be a string in ISO format (YYYY-MM-DD)
        assert isinstance(dob, str)
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', dob)
        
        # DOB should be within reasonable age range (default 18-90)
        today = datetime.date.today()
        dob_date = datetime.date.fromisoformat(dob)
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        assert 18 <= age <= 90
        
        # Test with custom age range
        young_dob = generator.generate_dob(min_age=5, max_age=10)
        young_dob_date = datetime.date.fromisoformat(young_dob)
        young_age = today.year - young_dob_date.year - ((today.month, today.day) < (young_dob_date.month, young_dob_date.day))
        assert 5 <= young_age <= 10
    
    def test_generate_ssn(self):
        """Test SSN generation."""
        generator = SyntheticDataGenerator()
        ssn = generator.generate_ssn()
        
        # SSN should be a string in format XXX-XX-XXXX
        assert isinstance(ssn, str)
        assert re.match(r'^\d{3}-\d{2}-\d{4}$', ssn)
        
        # First part should be between 100-899
        first_part = int(ssn.split('-')[0])
        assert 100 <= first_part <= 899
    
    def test_generate_phone(self):
        """Test phone number generation."""
        generator = SyntheticDataGenerator()
        phone = generator.generate_phone()
        
        # Phone should be a string in format XXX-XXX-XXXX
        assert isinstance(phone, str)
        assert re.match(r'^\d{3}-\d{3}-\d{4}$', phone)
        
        # Area code should be between 200-999
        area_code = int(phone.split('-')[0])
        assert 200 <= area_code <= 999
    
    def test_generate_email(self):
        """Test email generation."""
        generator = SyntheticDataGenerator()
        
        # Test with automatic name
        email = generator.generate_email()
        assert isinstance(email, str)
        assert re.match(r'^[a-z\.]+@[a-z\.]+\.[a-z]{2,}$', email)
        
        # Test with provided name
        name = "John Smith"
        email = generator.generate_email(name)
        assert email.startswith("john.smith@")
    
    def test_generate_address(self):
        """Test address generation."""
        generator = SyntheticDataGenerator()
        address = generator.generate_address()
        
        # Address should be a dictionary with the expected keys
        assert isinstance(address, dict)
        assert "street" in address
        assert "city" in address
        assert "state" in address
        assert "zip" in address
        
        # Zip should be 5 digits
        assert re.match(r'^\d{5}$', address["zip"])
        
        # State should be a two-letter code
        assert re.match(r'^[A-Z]{2}$', address["state"])
    
    def test_generate_insurance_info(self):
        """Test insurance info generation."""
        generator = SyntheticDataGenerator()
        insurance = generator.generate_insurance_info()
        
        # Insurance should be a dictionary with the expected keys
        assert isinstance(insurance, dict)
        assert "provider" in insurance
        assert "id" in insurance
        assert "group" in insurance
        assert "plan_type" in insurance
        
        # Provider should be from the list of insurance companies
        # Insurance ID should have format XXNNNNNNNN
        assert re.match(r'^[A-Z]{2}\d{8}$', insurance["id"])
        
        # Group should have format G-NNNNNN
        assert re.match(r'^G-\d{6}$', insurance["group"])
    
    def test_generate_medical_record(self):
        """Test medical record generation."""
        generator = SyntheticDataGenerator()
        record = generator.generate_medical_record()
        
        # Record should be a dictionary with expected top-level keys
        assert isinstance(record, dict)
        assert "patient_id" in record
        assert "name" in record
        assert "gender" in record
        assert "dob" in record
        assert "ssn" in record
        assert "contact" in record
        assert "insurance" in record
        assert "medical_info" in record
        assert "visits" in record
        assert "next_appointment" in record
        
        # Check nested structures
        assert isinstance(record["contact"], dict)
        assert isinstance(record["insurance"], dict)
        assert isinstance(record["medical_info"], dict)
        assert isinstance(record["visits"], list)
        
        # Medical info should have conditions and medications
        assert "conditions" in record["medical_info"]
        assert "medications" in record["medical_info"]
        assert isinstance(record["medical_info"]["conditions"], list)
        assert isinstance(record["medical_info"]["medications"], list)
        
        # Verify some data types and formats
        assert re.match(r'^P\d{8}$', record["patient_id"])
        assert record["gender"] in ["Male", "Female", "Other"]
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', record["dob"])
        assert re.match(r'^\d{3}-\d{2}-\d{4}$', record["ssn"])
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', record["next_appointment"])
    
    def test_generate_dataset(self):
        """Test dataset generation."""
        generator = SyntheticDataGenerator()
        
        # Test default size
        dataset = generator.generate_dataset()
        assert isinstance(dataset, list)
        assert len(dataset) == 10
        
        # Test custom size
        custom_size = 5
        dataset = generator.generate_dataset(num_records=custom_size)
        assert len(dataset) == custom_size
        
        # Each record should be a valid medical record
        for record in dataset:
            assert isinstance(record, dict)
            assert "patient_id" in record
            assert "name" in record
    
    def test_generate_llm_safe_example(self):
        """Test LLM-safe example generation."""
        generator = SyntheticDataGenerator()
        record = generator.generate_llm_safe_example()
        
        # Record should have simplified fields for LLM use
        assert isinstance(record, dict)
        assert "id" in record
        assert "name" in record
        assert "age" in record
        assert "gender" in record
        assert "chief_complaint" in record
        assert "diagnosis" in record
        assert "medications" in record
        
        # Verify data types and values
        assert isinstance(record["id"], str)
        assert isinstance(record["name"], str)
        assert isinstance(record["age"], int)
        assert 25 <= record["age"] <= 75
        assert record["gender"] in ["male", "female"]
        assert record["diagnosis"] in MEDICAL_CONDITIONS
        
        # Medications should be a list of valid medications
        assert isinstance(record["medications"], list)
        for med in record["medications"]:
            assert med in MEDICATIONS
    
    def test_add_watermark(self):
        """Test adding watermark to data."""
        generator = SyntheticDataGenerator()
        data = {"name": "John Smith"}
        
        watermarked = generator.add_watermark(data)
        
        # Original data should be preserved
        assert watermarked["name"] == "John Smith"
        
        # Watermark should be added
        assert "_synthetic" in watermarked
        assert "disclaimer" in watermarked["_synthetic"]
        assert "generated" in watermarked["_synthetic"]
        assert "generator" in watermarked["_synthetic"]
        
        # Disclaimer should indicate synthetic data
        assert "SYNTHETIC DATA" in watermarked["_synthetic"]["disclaimer"]
        assert "NOT REAL PHI" in watermarked["_synthetic"]["disclaimer"]
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_to_file(self, mock_json_dump, mock_file_open):
        """Test saving data to file."""
        generator = SyntheticDataGenerator()
        data = {"name": "John Smith"}
        file_path = "test_output.json"
        
        generator.save_to_file(data, file_path)
        
        # File should be opened for writing
        mock_file_open.assert_called_once_with(file_path, 'w')
        
        # JSON dump should be called with the data and indent
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        assert args[0] == data
        assert kwargs.get("indent") == 2

class TestConvenienceFunctions:
    """Tests for the convenience functions."""
    
    def test_generate_demo_patient(self):
        """Test generate_demo_patient function."""
        patient = generate_demo_patient()
        
        # Should be a dictionary with watermark
        assert isinstance(patient, dict)
        assert "_synthetic" in patient
        
        # Should have expected fields
        assert "name" in patient
        assert "gender" in patient
        assert "dob" in patient
        assert "ssn" in patient
        assert "medical_info" in patient
    
    @patch("hipaah.utils.synthetic_data.SyntheticDataGenerator.save_to_file")
    def test_generate_sample_dataset(self, mock_save):
        """Test generate_sample_dataset function."""
        # Test without file path
        dataset = generate_sample_dataset(num_records=3)
        
        # Should be a list of watermarked records
        assert isinstance(dataset, list)
        assert len(dataset) == 3
        for record in dataset:
            assert "_synthetic" in record
        
        # save_to_file should not be called
        mock_save.assert_not_called()
        
        # Test with file path
        file_path = "test_dataset.json"
        dataset = generate_sample_dataset(num_records=2, file_path=file_path)
        
        # save_to_file should be called with the dataset and path
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        assert len(args[0]) == 2  # dataset with 2 records
        assert args[1] == file_path
    
    def test_transform_real_to_synthetic(self):
        """Test transform_real_to_synthetic function."""
        # Create a realistic patient record
        real_record = {
            "name": "Real Patient",
            "dob": "1975-05-15",
            "ssn": "123-45-6789",
            "phone": "555-123-4567",
            "email": "real.patient@example.com",
            "diagnosis": "Actual Condition",
            "medications": ["Real Med 1", "Real Med 2"],
            "notes": "Real notes about the patient",
            "medical_history": {
                "previous_conditions": ["Condition 1", "Condition 2"],
                "surgeries": [
                    {"date": "2020-01-15", "procedure": "Surgery 1"}
                ]
            },
            "visit_count": 5,
            "last_visit": "2023-01-15"
        }
        
        # Transform to synthetic
        synthetic = transform_real_to_synthetic(real_record)
        
        # Should be watermarked
        assert "_synthetic" in synthetic
        
        # PHI fields should be transformed
        assert synthetic["name"] != "Real Patient"
        assert synthetic["ssn"] != "123-45-6789"
        assert synthetic["phone"] != "555-123-4567"
        assert synthetic["email"] != "real.patient@example.com"
        
        # Medical data should be transformed
        assert synthetic["diagnosis"] != "Actual Condition"
        assert synthetic["medications"] != ["Real Med 1", "Real Med 2"]
        
        # Complex nested data should be transformed
        assert synthetic["medical_history"]["previous_conditions"] != ["Condition 1", "Condition 2"]
        
        # Non-PHI fields should be preserved
        assert synthetic["visit_count"] == 5