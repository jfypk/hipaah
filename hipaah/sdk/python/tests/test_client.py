import pytest
import os
import json
from unittest.mock import patch, MagicMock
from hipaah import HipaahClient, PolicyRequest

# Define constants
MASKED = "***"

class TestHipaahClient:
    
    def test_init(self, policy_file):
        """Test HipaahClient initialization."""
        # Test with policy file
        client = HipaahClient(policy_file)
        assert client.policies is not None
        
        # Test without policy file
        client = HipaahClient()
        assert client.policies is None
    
    def test_load_policy(self, policy_file):
        """Test policy loading."""
        client = HipaahClient()
        policies = client.load_policy(policy_file)
        
        assert policies is not None
        assert len(policies) > 0
        assert policies[0].get('role') == 'receptionist'
        
        # Test with non-existent file
        with pytest.raises(Exception):
            client.load_policy("nonexistent_file.yaml")
    
    def test_evaluate(self, policy_file, sample_resource):
        """Test policy evaluation."""
        client = HipaahClient(policy_file)
        
        # Test receptionist with active shift
        result = client.evaluate(
            sample_resource, 
            "receptionist", 
            "treatment", 
            {"active_shift_only": True}
        )
        
        # Should allow these fields
        assert result.get("name") == sample_resource["name"]
        assert result.get("dob") == sample_resource["dob"]
        assert result.get("appointment_time") == sample_resource["appointment_time"]
        
        # Should mask these fields
        assert result.get("diagnosis") == MASKED
        assert result.get("notes") == MASKED
        
        # Should deny these fields
        assert "insurance_number" not in result
        
        # Test nurse
        result = client.evaluate(sample_resource, "nurse", "treatment")
        
        # Should allow these fields
        assert result.get("name") == sample_resource["name"]
        assert result.get("diagnosis") == sample_resource["diagnosis"]
        assert result.get("notes") == sample_resource["notes"]
        
        # Should mask these fields
        assert result.get("insurance_number") == MASKED
        
        # Test doctor (wildcard allow)
        result = client.evaluate(sample_resource, "doctor", "treatment")
        
        # Should allow all fields
        for key, value in sample_resource.items():
            assert result.get(key) == value
    
    def test_evaluate_with_conditions(self, policy_file, sample_resource):
        """Test policy evaluation with conditions."""
        client = HipaahClient(policy_file)
        
        # Test with condition that will pass
        result = client.evaluate(
            sample_resource, 
            "receptionist", 
            "treatment", 
            {"active_shift_only": True}
        )
        assert result.get("name") == sample_resource["name"]
        
        # Test with condition that will fail
        result = client.evaluate(
            sample_resource, 
            "receptionist", 
            "treatment", 
            {"active_shift_only": False}
        )
        assert len(result) == 0  # Empty result when conditions don't match
    
    def test_evaluate_with_justification(self, policy_file, sample_resource):
        """Test policy evaluation with justification."""
        client = HipaahClient(policy_file)
        
        # Test with billing_admin which has justification_ttl
        result = client.evaluate(
            sample_resource, 
            "billing_admin", 
            "billing", 
            {"justification": "Monthly billing review"}
        )
        
        # Should have meta data with expiry
        assert "_meta" in result
        assert "expires_at" in result.get("_meta", {})
    
    def test_evaluate_non_existent_policy(self, policy_file, sample_resource):
        """Test policy evaluation with non-existent policy."""
        client = HipaahClient(policy_file)
        
        # Test with non-existent role/intent
        result = client.evaluate(
            sample_resource, 
            "non_existent_role", 
            "non_existent_intent"
        )
        assert len(result) == 0  # Empty result when no matching policy
    
    def test_evaluate_no_policies_loaded(self, sample_resource):
        """Test evaluate with no policies loaded."""
        client = HipaahClient()
        
        # Should raise exception
        with pytest.raises(ValueError, match="No policies loaded"):
            client.evaluate(sample_resource, "doctor", "treatment")
            
    def test_batch_evaluate(self, policy_file, sample_resource):
        """Test batch evaluation of resources."""
        client = HipaahClient(policy_file)
        
        # Create a list of resources
        resources = [
            sample_resource,
            {**sample_resource, "name": "John Doe"},
            {**sample_resource, "diagnosis": "Hypertension"}
        ]
        
        # Evaluate batch as nurse
        results = client.batch_evaluate(resources, "nurse", "treatment")
        
        # Should return a list of the same length
        assert len(results) == len(resources)
        
        # Each result should be processed according to policy
        for i, result in enumerate(results):
            assert result.get("name") == resources[i]["name"]
            assert result.get("diagnosis") == resources[i]["diagnosis"]
            assert result.get("insurance_number") == MASKED
            
    def test_integration_with_policy_request(self, policy_file, sample_resource):
        """Test integration with PolicyRequest object."""
        client = HipaahClient(policy_file)
        
        # Create a policy request manually
        request = PolicyRequest(
            role="nurse",
            intent="treatment",
            attributes={},
            resource=sample_resource
        )
        
        # Use the private method that takes a PolicyRequest
        result = client._evaluate_policy(request, client.policies)
        
        # Verify same results as public method
        assert result.get("name") == sample_resource["name"]
        assert result.get("diagnosis") == sample_resource["diagnosis"]
        assert result.get("insurance_number") == MASKED