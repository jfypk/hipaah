import datetime
from typing import Dict, Any, Union, List
from hipaah.core.types import PolicyRequest

MASKED = "***"

def evaluate(resource: dict, role: str, intent: str, attributes: dict, policies: list) -> dict:
    """
    Evaluate access to a resource based on role, intent, and attributes.
    
    Args:
        resource: The resource to evaluate
        role: The user role
        intent: The intent of access
        attributes: Additional attributes for policy evaluation
        policies: List of policies to evaluate against
        
    Returns:
        Filtered resource with appropriate fields allowed, masked, or denied
    """
    for policy in policies:
        if policy.role != role or policy.intent != intent:
            continue

        # Evaluate attributes like shift
        if not all(attributes.get(k) == v for k, v in policy.conditions.items()):
            continue

        # Apply policy
        result = {}
        for key, value in resource.items():
            if key in policy.deny:
                continue
            elif key in policy.mask:
                result[key] = MASKED
            elif policy.allow == "*" or key in policy.allow:
                result[key] = value
                
        # Add expiry metadata if justification provided
        if attributes.get("justification") and hasattr(policy, "justification_ttl") and policy.justification_ttl:
            expires_at = datetime.datetime.now() + datetime.timedelta(minutes=policy.justification_ttl)
            result["_meta"] = {
                "expires_at": expires_at.isoformat()
            }
            
        return result

    # Default deny-all
    return {}

def evaluate_policy(request: Union[PolicyRequest, Dict[str, Any]], policies: List) -> Dict[str, Any]:
    """
    Evaluate access using a PolicyRequest object.
    
    This is a wrapper around the evaluate function that takes a PolicyRequest object
    for easier use in the SDK.
    
    Args:
        request: Either a PolicyRequest object or a dict with role, intent, attributes, and resource
        policies: List of policies to evaluate against
        
    Returns:
        Filtered resource with appropriate fields allowed, masked, or denied
    """
    # Handle input as either PolicyRequest object or dict
    if isinstance(request, dict):
        role = request.get("role")
        intent = request.get("intent")
        attributes = request.get("attributes", {})
        resource = request.get("resource", {})
    else:
        role = request.role
        intent = request.intent
        attributes = request.attributes
        resource = request.resource
        
    return evaluate(resource, role, intent, attributes, policies)
