from hipaah.core.engine import evaluate_policy
from hipaah.core.policy_loader import load_policies
from hipaah.core.types import PolicyRequest
from hipaah.utils.logger import SafeLogger
import json
import os

class HipaahClient:
    """Main client class for interacting with the HIPAAH SDK."""
    
    def __init__(self, policy_path=None, logger=None):
        """Initialize the HIPAAH client.
        
        Args:
            policy_path: Optional path to a policy file to load at initialization
            logger: Optional logger instance
        """
        self.policies = None
        self.logger = logger or SafeLogger()
        
        if policy_path:
            self.policies = load_policies(policy_path)
        
    def load_policy(self, policy_path):
        """Load policies from a file.
        
        Args:
            policy_path: Path to the policy file
            
        Returns:
            The loaded policies
        """
        self.policies = load_policies(policy_path)
        return self.policies
    
    def evaluate(self, resource, role, intent, attributes=None):
        """Evaluate a resource against loaded policies.
        
        Args:
            resource: The resource to evaluate
            role: The user role
            intent: The access intent
            attributes: Optional attributes for policy evaluation. If includes 'justification',
                        and policy has 'justification_ttl', the result will include expiry time
            
        Returns:
            The result of policy evaluation with optional expiry metadata
        """
        if not self.policies:
            raise ValueError("No policies loaded. Call load_policy first.")
            
        request = PolicyRequest(
            role=role,
            intent=intent,
            attributes=attributes or {},
            resource=resource
        )
        
        result = evaluate_policy(request, self.policies)
        
        # Log justification if provided
        if attributes and attributes.get("justification"):
            justification = attributes.get("justification")
            resource_id = str(resource.get("id", "unknown"))
            self.logger.info(
                f"Justification provided for {role}/{intent}",
                {"justification": justification, "resource_id": resource_id}
            )
            
            # Check if we have time-limited access
            if "_meta" in result and "expires_at" in result["_meta"]:
                expires_at = result["_meta"]["expires_at"]
                self.logger.info(
                    f"Time-limited access granted until {expires_at}",
                    {"role": role, "intent": intent, "resource_id": resource_id}
                )
        
        self.logger.info(f"Policy evaluation for {role}/{intent}", {"result": "success"})
        return result
        
    def _evaluate_policy(self, request, policies):
        """Internal method to evaluate policies using the evaluate_policy function.
        
        This method is called by evaluate() and is exposed for testing purposes.
        
        Args:
            request: PolicyRequest object with role, intent, attributes, and resource
            policies: List of policies to evaluate against
            
        Returns:
            The result of policy evaluation
        """
        return evaluate_policy(request, policies)
    
    def batch_evaluate(self, resources, role, intent, attributes=None):
        """Evaluate multiple resources against loaded policies.
        
        Args:
            resources: List of resources to evaluate
            role: The user role
            intent: The access intent
            attributes: Optional attributes for policy evaluation
            
        Returns:
            List of policy evaluation results
        """
        return [self.evaluate(resource, role, intent, attributes) for resource in resources]

class ApiClient(HipaahClient):
    """Client for interacting with the HIPAAH API."""
    
    def __init__(self, api_url, api_key=None, policy_path=None, logger=None):
        """Initialize the API client.
        
        Args:
            api_url: URL of the HIPAAH API
            api_key: Optional API key for authentication
            policy_path: Optional path to a policy file for local evaluation
            logger: Optional logger instance
        """
        super().__init__(policy_path, logger)
        self.api_url = api_url
        self.api_key = api_key or os.environ.get("HIPAAH_API_KEY")
        
    def remote_evaluate(self, resource, role, intent, attributes=None):
        """Evaluate a resource against the remote API.
        
        In a real implementation, this would make an HTTP request to the API.
        For now, it falls back to local evaluation.
        
        Args:
            resource: The resource to evaluate
            role: The user role
            intent: The access intent
            attributes: Optional attributes for policy evaluation
            
        Returns:
            The result of policy evaluation
        """
        # In a real implementation, this would use requests or httpx to call the API
        self.logger.info(f"Remote evaluation for {role}/{intent}", {"api_url": self.api_url})
        
        # For now, fall back to local evaluation
        return self.evaluate(resource, role, intent, attributes)