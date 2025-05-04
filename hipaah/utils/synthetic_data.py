"""
Synthetic data generator for HIPAah.

This module provides utilities to generate realistic but fake PHI data
for demos, screenshots, and testing purposes.
"""

import random
import string
import datetime
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Tuple

# Common demo-friendly names
FIRST_NAMES = [
    "John", "Lisa", "Michael", "Sarah", "David", "Emma", "James", "Olivia",
    "Robert", "Maria", "William", "Jennifer", "Carlos", "Jessica", "Daniel",
    "Anna", "Matthew", "Emily", "Christopher", "Sofia", "Alexander", "Ava",
    "Ryan", "Isabella", "Michelle", "Jacob", "Nicole", "Andrew", "Samantha"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas",
    "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez",
    "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Robinson", "Walker",
    "Perez", "Hall", "Young", "Allen", "Sanchez", "Wright", "King", "Scott"
]

# Common medical conditions for demo data
MEDICAL_CONDITIONS = [
    "Hypertension", "Type 2 Diabetes", "Asthma", "Migraine", "Anxiety Disorder",
    "Depression", "Allergic Rhinitis", "Osteoarthritis", "GERD", "Hypothyroidism",
    "Back Pain", "Insomnia", "Hyperlipidemia", "Vitamin D Deficiency",
    "Obesity", "Chronic Sinusitis", "Iron Deficiency Anemia", "Seasonal Allergies"
]

# Common medications for demo data
MEDICATIONS = [
    "Lisinopril", "Metformin", "Levothyroxine", "Amlodipine", "Metoprolol",
    "Atorvastatin", "Omeprazole", "Simvastatin", "Losartan", "Albuterol",
    "Gabapentin", "Hydrochlorothiazide", "Sertraline", "Montelukast",
    "Pantoprazole", "Fluticasone", "Escitalopram", "Acetaminophen", "Ibuprofen"
]

# Demo insurance companies
INSURANCE_COMPANIES = [
    "Blue Cross", "Aetna", "UnitedHealthcare", "Cigna", "Humana",
    "Kaiser", "Anthem", "Health Net", "MetLife", "Centene"
]

class SyntheticDataGenerator:
    """Generator for synthetic healthcare data."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the synthetic data generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
    
    def generate_name(self) -> str:
        """Generate a random full name."""
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        return f"{first} {last}"
    
    def generate_dob(self, min_age: int = 18, max_age: int = 90) -> str:
        """
        Generate a random date of birth.
        
        Args:
            min_age: Minimum age in years
            max_age: Maximum age in years
            
        Returns:
            Date of birth in ISO format (YYYY-MM-DD)
        """
        today = datetime.date.today()
        
        # Calculate date range based on age range
        min_date = today.replace(year=today.year - max_age)
        max_date = today.replace(year=today.year - min_age)
        
        # Generate random date in range
        days_range = (max_date - min_date).days
        random_days = random.randint(0, days_range)
        dob = min_date + datetime.timedelta(days=random_days)
        
        return dob.isoformat()
    
    def generate_ssn(self) -> str:
        """Generate a random US Social Security Number."""
        area = random.randint(100, 899)
        group = random.randint(10, 99)
        serial = random.randint(1000, 9999)
        return f"{area}-{group}-{serial}"
    
    def generate_phone(self) -> str:
        """Generate a random US phone number."""
        area = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"{area}-{prefix}-{line}"
    
    def generate_email(self, name: Optional[str] = None) -> str:
        """
        Generate a random email address.
        
        Args:
            name: Optional name to use in email (otherwise randomly generated)
            
        Returns:
            A synthetic email address
        """
        if name is None:
            name = self.generate_name()
        
        # Replace spaces with dots and make lowercase
        name_part = name.lower().replace(" ", ".")
        
        # Common email domains
        domains = ["example.com", "demo.org", "test.net", "sample.edu", "mock.io"]
        domain = random.choice(domains)
        
        return f"{name_part}@{domain}"
    
    def generate_address(self) -> Dict[str, str]:
        """Generate a random US address."""
        # Street types
        street_types = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Way", "Pl", "Ct"]
        
        # Street names - common but fictional
        street_names = [
            "Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", 
            "Lake", "Hill", "Park", "Spring", "Sunset", "Highland", "Valley",
            "Meadow", "Forest", "River", "Mountain", "Ocean"
        ]
        
        # Cities - fictional or generic
        cities = [
            "Springfield", "Riverdale", "Lakeside", "Maplewood", "Oakville",
            "Centerville", "Liberty", "Fairview", "Georgetown", "Salem",
            "Newport", "Kingston", "Burlington", "Bristol", "Arlington"
        ]
        
        # States
        states = [
            "CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
            "NJ", "VA", "WA", "AZ", "MA", "IN", "TN", "MO", "MD", "WI"
        ]
        
        street_num = random.randint(100, 9999)
        street_name = random.choice(street_names)
        street_type = random.choice(street_types)
        city = random.choice(cities)
        state = random.choice(states)
        zip_code = f"{random.randint(10000, 99999)}"
        
        return {
            "street": f"{street_num} {street_name} {street_type}",
            "city": city,
            "state": state,
            "zip": zip_code
        }
    
    def generate_insurance_info(self) -> Dict[str, str]:
        """Generate random health insurance information."""
        company = random.choice(INSURANCE_COMPANIES)
        
        # Generate insurance ID with a mix of letters and numbers
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=8))
        insurance_id = f"{letters}{numbers}"
        
        # Generate group number
        group_number = f"G-{''.join(random.choices(string.digits, k=6))}"
        
        return {
            "provider": company,
            "id": insurance_id,
            "group": group_number,
            "plan_type": random.choice(["PPO", "HMO", "EPO", "POS", "HDHP"])
        }
    
    def generate_medical_record(self) -> Dict[str, Any]:
        """Generate a synthetic medical record with common fields."""
        patient_id = f"P{''.join(random.choices(string.digits, k=8))}"
        name = self.generate_name()
        gender = random.choice(["Male", "Female", "Other"])
        dob = self.generate_dob()
        
        # Generate between 1-3 medical conditions
        num_conditions = random.randint(1, 3)
        conditions = random.sample(MEDICAL_CONDITIONS, num_conditions)
        
        # Generate between 1-5 medications
        num_medications = random.randint(1, 5)
        medications = random.sample(MEDICATIONS, num_medications)
        
        # Generate recent visit date
        today = datetime.date.today()
        days_ago = random.randint(1, 90)
        last_visit = (today - datetime.timedelta(days=days_ago)).isoformat()
        
        # Generate next appointment
        days_ahead = random.randint(1, 60)
        next_appointment = (today + datetime.timedelta(days=days_ahead)).isoformat()
        
        # Common blood pressure values
        systolic = random.randint(100, 160)
        diastolic = random.randint(60, 100)
        
        return {
            "patient_id": patient_id,
            "name": name,
            "gender": gender,
            "dob": dob,
            "ssn": self.generate_ssn(),
            "contact": {
                "phone": self.generate_phone(),
                "email": self.generate_email(name),
                "address": self.generate_address()
            },
            "insurance": self.generate_insurance_info(),
            "medical_info": {
                "conditions": conditions,
                "medications": medications,
                "allergies": random.sample(["Penicillin", "Peanuts", "Shellfish", "Latex", "None"], 
                                          random.randint(0, 2)),
                "blood_type": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                "height_cm": random.randint(150, 200),
                "weight_kg": random.randint(50, 100),
                "blood_pressure": f"{systolic}/{diastolic}"
            },
            "visits": [
                {
                    "date": last_visit,
                    "provider": f"Dr. {random.choice(LAST_NAMES)}",
                    "reason": random.choice(["Annual check-up", "Follow-up", "Acute illness", "Chronic condition management"]),
                    "notes": "Patient reports feeling well overall with minor concerns about sleep quality."
                }
            ],
            "next_appointment": next_appointment
        }
    
    def generate_dataset(self, num_records: int = 10) -> List[Dict[str, Any]]:
        """
        Generate a dataset of synthetic medical records.
        
        Args:
            num_records: Number of records to generate
            
        Returns:
            List of synthetic medical records
        """
        return [self.generate_medical_record() for _ in range(num_records)]
    
    def generate_llm_safe_example(self) -> Dict[str, Any]:
        """
        Generate a simplified record that's safe to use in LLM prompts.
        
        Returns:
            A simplified medical record with minimal PHI
        """
        name = self.generate_name()
        age = random.randint(25, 75)
        gender = random.choice(["male", "female"])
        
        # Pick 1-2 conditions
        conditions = random.sample(MEDICAL_CONDITIONS, random.randint(1, 2))
        
        # Generate simplified record with less PHI
        return {
            "id": str(uuid.uuid4())[:8],  # Short ID instead of patient ID
            "name": name,
            "age": age,
            "gender": gender,
            "chief_complaint": random.choice([
                "Chest pain", "Shortness of breath", "Headache", 
                "Abdominal pain", "Back pain", "Fatigue"
            ]),
            "diagnosis": conditions[0],
            "medications": random.sample(MEDICATIONS, random.randint(1, 3))
        }

    def add_watermark(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a watermark to synthetic data to clearly mark it as non-PHI.
        
        Args:
            data: The synthetic data to watermark
            
        Returns:
            Data with added watermark metadata
        """
        result = data.copy()
        result["_synthetic"] = {
            "generated": datetime.datetime.now().isoformat(),
            "disclaimer": "SYNTHETIC DATA - NOT REAL PHI - FOR DEMO PURPOSES ONLY",
            "generator": "HIPAah SyntheticDataGenerator"
        }
        return result
    
    def save_to_file(self, data: Any, file_path: str) -> None:
        """
        Save synthetic data to a JSON file.
        
        Args:
            data: The synthetic data to save
            file_path: Path to save the file
            
        Returns:
            None
        """
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved synthetic data to {file_path}")

# Convenience functions
def generate_demo_patient() -> Dict[str, Any]:
    """Generate a single demo patient record with watermark."""
    generator = SyntheticDataGenerator()
    patient = generator.generate_medical_record()
    return generator.add_watermark(patient)

def generate_sample_dataset(num_records: int = 10, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate a sample dataset of synthetic records.
    
    Args:
        num_records: Number of records to generate
        file_path: Optional path to save the dataset
        
    Returns:
        List of synthetic records
    """
    generator = SyntheticDataGenerator()
    dataset = generator.generate_dataset(num_records)
    dataset = [generator.add_watermark(record) for record in dataset]
    
    if file_path:
        generator.save_to_file(dataset, file_path)
        
    return dataset

def transform_real_to_synthetic(
    real_record: Dict[str, Any], 
    preserve_structure: bool = True
) -> Dict[str, Any]:
    """
    Transform a real patient record into a synthetic one.
    
    This preserves the structure but replaces all PHI with synthetic values.
    
    Args:
        real_record: The real record to transform
        preserve_structure: Whether to preserve the exact structure
        
    Returns:
        A synthetic record with the same structure as the original
    """
    generator = SyntheticDataGenerator()
    
    def _process_value(key: str, value: Any) -> Any:
        """Process a value based on its field name and type."""
        # Common field name patterns
        if isinstance(value, str):
            if any(key.lower().endswith(suffix) for suffix in ["name", "patient"]):
                return generator.generate_name()
            elif any(key.lower().endswith(suffix) for suffix in ["dob", "birth", "birthdate"]):
                return generator.generate_dob()
            elif any(key.lower().endswith(suffix) for suffix in ["ssn", "social"]):
                return generator.generate_ssn()
            elif any(key.lower().endswith(suffix) for suffix in ["phone", "mobile", "cell"]):
                return generator.generate_phone()
            elif any(key.lower().endswith(suffix) for suffix in ["email"]):
                return generator.generate_email()
            elif any(key.lower().endswith(suffix) for suffix in ["diagnosis", "condition"]):
                return random.choice(MEDICAL_CONDITIONS)
            elif any(key.lower().endswith(suffix) for suffix in ["medication", "med", "drug", "prescription"]):
                return random.choice(MEDICATIONS)
            else:
                # For other string fields, preserve length and character types
                if len(value) < 5:
                    return value  # Preserve very short strings
                return "SYNTH_" + "".join(random.choices(string.ascii_letters + string.digits, k=len(value) - 6))
        
        # Handle dictionaries recursively
        elif isinstance(value, dict):
            return {k: _process_value(k, v) for k, v in value.items()}
        
        # Handle lists recursively
        elif isinstance(value, list):
            if len(value) > 0:
                if all(isinstance(item, dict) for item in value):
                    # List of dictionaries
                    return [_process_value("item", item) for item in value]
                elif all(isinstance(item, str) for item in value):
                    # List of strings - if they look like medications or conditions
                    if any(key.lower().endswith(suffix) for suffix in ["medications", "meds", "drugs"]):
                        return random.sample(MEDICATIONS, min(len(value), len(MEDICATIONS)))
                    elif any(key.lower().endswith(suffix) for suffix in ["conditions", "diagnoses", "problems"]):
                        return random.sample(MEDICAL_CONDITIONS, min(len(value), len(MEDICAL_CONDITIONS)))
                    else:
                        return [f"SYNTH_{i}" for i in range(len(value))]
            return value
        
        # For numbers, dates, etc.
        else:
            return value
    
    # Transform the record
    synthetic = _process_value("root", real_record)
    
    # Add watermark
    return generator.add_watermark(synthetic)

# Create a global instance for easy importing
default_generator = SyntheticDataGenerator()