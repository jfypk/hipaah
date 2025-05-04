from hipaah import HipaahClient, SafeLogger
import json

print("HIPAah Python SDK Example")
print("========================")

# Create a client instance with the policy file
client = HipaahClient("/Users/jpark/Code/hipaah/config/sample_policies/example_policy.yaml")

# Resource data (patient info)
resource = {
    "id": "P12345",
    "name": "Lisa Chang",
    "dob": "1983-09-22",
    "diagnosis": "Asthma",
    "insurance_number": "123-45-6789",
    "appointment_time": "2025-05-10T09:30:00Z",
    "notes": "Patient reports shortness of breath during physical activity",
    "medications": ["Albuterol", "Fluticasone"],
    "billing_codes": ["J45.909", "Z79.51"]
}

# Setup safe logging
logger = SafeLogger(
    masked_fields=["diagnosis", "insurance_number", "notes"],
    log_file_path="./example_logs.jsonl",
    justification_log_path="./example_justifications.jsonl"
)

print("\nExample 1: Basic Policy Evaluation")
print("----------------------------------")
# Basic policy evaluation for receptionist
role = "receptionist"
intent = "treatment"
attributes = {"active_shift_only": True}

# Evaluate the policy
receptionist_view = client.evaluate(resource, role, intent, attributes)

# Pretty print the filtered results
print(f"Receptionist view of patient record: {json.dumps(receptionist_view, indent=2)}")

# Safely log the result
logger.info("Receptionist accessed patient record", {"patient_id": resource["id"]})

print("\nExample 2: Time-Limited Justification")
print("------------------------------------")
# Policy evaluation with justification for billing admin
role = "billing_admin"
intent = "billing"
attributes = {
    "justification": "Monthly insurance claim processing"
}

# Evaluate the policy with justification
billing_view = client.evaluate(resource, role, intent, attributes)

# Pretty print the results with metadata
print(f"Billing admin view with justification: {json.dumps(billing_view, indent=2)}")

# Explicitly log the justification
expires_at = billing_view.get("_meta", {}).get("expires_at") if "_meta" in billing_view else None
logger.justification(
    role=role,
    intent=intent,
    resource_id=resource["id"],
    justification=attributes["justification"],
    expires_at=expires_at
)

print("\nExample 3: Doctor Access (Wildcard)")
print("----------------------------------")
# Policy evaluation for doctor (wildcard access)
role = "doctor"
intent = "treatment"

# Evaluate the policy
doctor_view = client.evaluate(resource, role, intent)

# Log the access
logger.info("Doctor accessed patient record", {"patient_id": resource["id"]})

# Print a summary of fields accessible
print(f"Doctor has access to {len(doctor_view)} fields: {', '.join(doctor_view.keys())}")

print("\nExample 4: Batch Evaluation")
print("--------------------------")
# Create a list of patient resources
patients = [
    {**resource, "id": "P12345", "name": "Lisa Chang"},
    {**resource, "id": "P23456", "name": "John Smith", "diagnosis": "Hypertension"},
    {**resource, "id": "P34567", "name": "Maria Rodriguez", "diagnosis": "Type 2 Diabetes"}
]

# Batch evaluate for nurse role
role = "nurse"
intent = "treatment"
nurse_views = client.batch_evaluate(patients, role, intent)

# Print summary of batch results
print(f"Processed {len(nurse_views)} patient records for {role}/{intent}")
print(f"First patient result: {json.dumps(nurse_views[0], indent=2)}")

print("\nLogs have been written to:")
print(f"- Log file: {logger.log_file_path}")
print(f"- Justification log: {logger.justification_log_path}")