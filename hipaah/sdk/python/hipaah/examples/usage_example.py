from hipaah import HipaahClient, SafeLogger

# Create a client instance with the policy file
client = HipaahClient("/Users/jpark/Code/hipaah/config/sample_policies/example_policy.yaml")

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

# Alternative usage - manual approach
"""
from hipaah import load_policies, evaluate_policy, PolicyRequest, SafeLogger

# Load the policies from file
policies = load_policies("/Users/jpark/Code/hipaah/config/sample_policies/example_policy.yaml")

# Create a request object
request = PolicyRequest(
    role="receptionist",
    intent="treatment",
    attributes={"active_shift_only": True},
    resource=resource
)

# Evaluate the policy
filtered = evaluate_policy(request, policies)

# Safely log the result
logger = SafeLogger(masked_fields=["diagnosis", "insurance_number"])
logger.info("Filtered output for UI rendering", filtered)
"""

# [INFO] Filtered output for UI rendering {'name': 'Lisa Chang', 'dob': '1983-09-22', 'diagnosis': '***'}