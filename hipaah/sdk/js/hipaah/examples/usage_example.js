const { HipaahClient, SafeLogger, maskPhiFields } = require('hipaah');

// Create a client instance with the policy file
const client = new HipaahClient('/Users/jpark/Code/hipaah/config/sample_policies/example_policy.yaml');

// Resource data (patient info)
const resource = {
  name: "Lisa Chang",
  dob: "1983-09-22",
  diagnosis: "Asthma",
  insurance_number: "123-45-6789"
};

// Policy evaluation parameters
const role = "receptionist";
const intent = "treatment";
const attributes = { active_shift_only: true };

// Evaluate the policy
const filtered = client.evaluate(resource, role, intent, attributes);

// Safely log the result, masking PHI fields
const logger = new SafeLogger(["diagnosis", "insurance_number"]);
logger.info("Filtered output for UI rendering", filtered);

// Alternative approach - direct masking
const maskedData = maskPhiFields(resource, ["diagnosis", "insurance_number"]);
console.log('Manually masked data:', maskedData);

// Batch processing example
const patientRecords = [
  {
    name: "John Smith",
    dob: "1990-03-14",
    diagnosis: "Diabetes",
    insurance_number: "234-56-7890"
  },
  {
    name: "Maria Rodriguez",
    dob: "1975-12-01",
    diagnosis: "Arthritis",
    insurance_number: "345-67-8901"
  }
];

// Process multiple records at once
const batchResults = client.batchEvaluate(patientRecords, role, intent, attributes);
console.log('Batch results:', batchResults);

// API client example (commented out since it's just for demonstration)
/*
const { ApiClient } = require('hipaah');

// Create API client
const apiClient = new ApiClient(
  'https://api.example.com/hipaah',
  'your-api-key',
  '/Users/jpark/Code/hipaah/config/sample_policies/example_policy.yaml'
);

// Use remote API for evaluation
async function evaluatePatientRecord() {
  try {
    const result = await apiClient.remoteEvaluate(
      resource,
      "nurse",
      "billing",
      { department: "cardiology" }
    );
    
    console.log("API result:", result);
  } catch (error) {
    console.error("API evaluation failed:", error);
  }
}

evaluatePatientRecord();
*/