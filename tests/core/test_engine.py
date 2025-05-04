import pytest
import datetime
import re
from hipaah.core.engine import evaluate, evaluate_policy, MASKED
from hipaah.core.policy_loader import Policy
from hipaah.core.types import PolicyRequest


class TestEngine:
    @pytest.fixture
    def sample_resource(self):
        return {
            "name": "John Doe",
            "dob": "1980-01-01",
            "diagnosis": "Hypertension",
            "notes": "Patient needs follow-up",
            "insurance_number": "INS12345",
            "appointment_time": "2023-11-15 10:00"
        }
    
    def test_evaluate_matching_policy(self, sample_resource):
        # Create a sample policy (similar to receptionist policy)
        policies = [
            Policy(
                role="receptionist",
                intent="treatment",
                allow=["name", "dob", "appointment_time"],
                mask=["diagnosis", "notes"],
                deny=["insurance_number"],
                conditions={"active_shift_only": True}
            )
        ]
        
        # Evaluate with matching conditions
        result = evaluate(
            resource=sample_resource,
            role="receptionist",
            intent="treatment",
            attributes={"active_shift_only": True},
            policies=policies
        )
        
        # Verify results
        assert "name" in result
        assert result["name"] == "John Doe"
        assert "dob" in result
        assert result["dob"] == "1980-01-01"
        assert "appointment_time" in result
        assert result["appointment_time"] == "2023-11-15 10:00"
        assert "diagnosis" in result
        assert result["diagnosis"] == MASKED
        assert "notes" in result
        assert result["notes"] == MASKED
        assert "insurance_number" not in result
    
    @pytest.mark.parametrize("test_case", [
        {
            "name": "non_matching_role",
            "resource": {"name": "John Doe", "diagnosis": "Hypertension"},
            "policy": Policy(
                role="nurse",
                intent="treatment",
                allow=["name", "diagnosis"],
                mask=[],
                deny=[],
                conditions={}
            ),
            "role": "receptionist",  # Different from policy's role
            "intent": "treatment",
            "attributes": {},
        },
        {
            "name": "non_matching_intent",
            "resource": {"name": "John Doe", "insurance_number": "INS12345"},
            "policy": Policy(
                role="billing_admin",
                intent="billing",
                allow=["name", "insurance_number"],
                mask=[],
                deny=[],
                conditions={}
            ),
            "role": "billing_admin",
            "intent": "treatment",  # Different from policy's intent
            "attributes": {},
        },
        {
            "name": "non_matching_condition",
            "resource": {"name": "John Doe", "dob": "1980-01-01"},
            "policy": Policy(
                role="receptionist",
                intent="treatment",
                allow=["name", "dob"],
                mask=[],
                deny=[],
                conditions={"active_shift_only": True}
            ),
            "role": "receptionist",
            "intent": "treatment",
            "attributes": {"active_shift_only": False},  # Doesn't match required condition
        },
    ])
    def test_policy_non_matches(self, test_case):
        """Test cases where policies don't match due to role, intent, or conditions."""
        # Evaluate with the specified parameters
        result = evaluate(
            resource=test_case["resource"],
            role=test_case["role"],
            intent=test_case["intent"],
            attributes=test_case["attributes"],
            policies=[test_case["policy"]]
        )
        
        # All non-matching cases should result in empty dict (deny all)
        assert result == {}
    
    def test_evaluate_wildcard_allow(self, sample_resource):
        # Create a policy with all fields explicitly allowed
        policies = [
            Policy(
                role="doctor",
                intent="treatment",
                allow=list(sample_resource.keys()),  # Explicitly list all keys
                mask=[],
                deny=[],
                conditions={}
            )
        ]
        
        # Evaluate with policy allowing all fields
        result = evaluate(
            resource=sample_resource,
            role="doctor",
            intent="treatment",
            attributes={},
            policies=policies
        )
        
        # Should get full resource (everything allowed)
        assert result == sample_resource
    
    @pytest.mark.parametrize("policies,expected", [
        (
            # Case 1: Multiple policies, first one matches (should mask diagnosis)
            [
                Policy(
                    role="nurse",
                    intent="treatment",
                    allow=["name"],
                    mask=["diagnosis"],
                    deny=[],
                    conditions={}
                ),
                Policy(
                    role="nurse",
                    intent="treatment",
                    allow=["name", "diagnosis"],  # More permissive
                    mask=[],
                    deny=[],
                    conditions={}
                )
            ],
            {"name": "John Doe", "diagnosis": MASKED}
        ),
        (
            # Case 2: No policies
            [],
            {}
        )
    ])
    def test_policy_evaluation_scenarios(self, policies, expected):
        """Test various policy evaluation scenarios."""
        resource = {"name": "John Doe", "diagnosis": "Hypertension"}
        
        result = evaluate(
            resource=resource,
            role="nurse",
            intent="treatment",
            attributes={},
            policies=policies
        )
        
        assert result == expected
        
    def test_time_limited_justification(self, sample_resource):
        """Test that justification_ttl creates time-limited access with expiry."""
        # Create a policy with justification_ttl
        policies = [
            Policy(
                role="billing_admin",
                intent="billing",
                allow=["name", "insurance_number"],
                mask=["diagnosis"],
                deny=[],
                conditions={},
                justification_ttl=60  # 60 minute expiry
            )
        ]
        
        # Evaluate with justification
        result = evaluate(
            resource=sample_resource,
            role="billing_admin",
            intent="billing",
            attributes={"justification": "Monthly billing review"},
            policies=policies
        )
        
        # Verify metadata with expiry is added
        assert "_meta" in result
        assert "expires_at" in result["_meta"]
        
        # Verify the expiry is in the future and formatted as ISO datetime
        expires_at = result["_meta"]["expires_at"]
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', expires_at)
        
        # Expiry should be about 60 minutes in the future (allow small variation for test time)
        expires_datetime = datetime.datetime.fromisoformat(expires_at)
        now = datetime.datetime.now()
        delta = expires_datetime - now
        assert 59 <= delta.total_seconds() / 60 <= 61
        
    def test_evaluate_policy_function(self, sample_resource):
        """Test the evaluate_policy function wrapper."""
        # Create a policy with justification_ttl
        policies = [
            Policy(
                role="billing_admin",
                intent="billing",
                allow=["name", "insurance_number"],
                mask=["diagnosis"],
                deny=[],
                conditions={},
                justification_ttl=60
            )
        ]
        
        # Test with PolicyRequest object
        request = PolicyRequest(
            role="billing_admin",
            intent="billing",
            attributes={"justification": "Monthly billing review"},
            resource=sample_resource
        )
        
        result = evaluate_policy(request, policies)
        
        # Verify results
        assert result["name"] == sample_resource["name"]
        assert result["insurance_number"] == sample_resource["insurance_number"]
        assert result["diagnosis"] == MASKED
        assert "_meta" in result
        assert "expires_at" in result["_meta"]
        
        # Test with dictionary input
        request_dict = {
            "role": "billing_admin",
            "intent": "billing",
            "attributes": {"justification": "Monthly billing review"},
            "resource": sample_resource
        }
        
        result = evaluate_policy(request_dict, policies)
        
        # Verify same results with dictionary input
        assert result["name"] == sample_resource["name"]
        assert result["insurance_number"] == sample_resource["insurance_number"]
        assert result["diagnosis"] == MASKED
        assert "_meta" in result
        assert "expires_at" in result["_meta"]
        
    def test_justification_without_ttl(self, sample_resource):
        """Test that justification without TTL doesn't add expiry metadata."""
        # Create a policy without justification_ttl
        policies = [
            Policy(
                role="nurse",
                intent="treatment",
                allow=["name", "diagnosis"],
                mask=["insurance_number"],
                deny=[],
                conditions={},
                # No justification_ttl
            )
        ]
        
        # Evaluate with justification
        result = evaluate(
            resource=sample_resource,
            role="nurse",
            intent="treatment",
            attributes={"justification": "Patient assessment"},
            policies=policies
        )
        
        # Should not add _meta data since no TTL defined
        assert "_meta" not in result
        
    def test_policy_with_ttl_but_no_justification(self, sample_resource):
        """Test that TTL without justification doesn't add expiry metadata."""
        # Create a policy with justification_ttl
        policies = [
            Policy(
                role="billing_admin",
                intent="billing",
                allow=["name", "insurance_number"],
                mask=["diagnosis"],
                deny=[],
                conditions={},
                justification_ttl=60
            )
        ]
        
        # Evaluate without justification
        result = evaluate(
            resource=sample_resource,
            role="billing_admin",
            intent="billing",
            attributes={},  # No justification
            policies=policies
        )
        
        # Should not add _meta data since no justification provided
        assert "_meta" not in result