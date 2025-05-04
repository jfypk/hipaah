import yaml
from typing import List, Dict, Any, Optional, Union

class Policy:
    def __init__(self, 
                 role: str, 
                 intent: str, 
                 allow: Union[List[str], str], 
                 mask: List[str], 
                 deny: List[str], 
                 conditions: Dict[str, Any] = None,
                 justification_ttl: Optional[int] = None):
        self.role = role
        self.intent = intent
        
        # Handle wildcard allow ('*')
        if allow == "*":
            self.allow = allow
        else:
            self.allow = set(allow)
            
        self.mask = set(mask)
        self.deny = set(deny)
        self.conditions = conditions or {}
        self.justification_ttl = justification_ttl

def load_policies(path: str) -> List[Policy]:
    """
    Load policies from a YAML file.
    
    Args:
        path: Path to the YAML policy file
        
    Returns:
        List of Policy objects
    """
    with open(path, 'r') as f:
        raw = yaml.safe_load(f)

    policies = []
    for rule in raw:
        policies.append(Policy(
            role=rule.get("role"),
            intent=rule.get("intent"),
            allow=rule.get("allow", []),
            mask=rule.get("mask", []),
            deny=rule.get("deny", []),
            conditions=rule.get("conditions", {}),
            justification_ttl=rule.get("justification_ttl")
        ))
    return policies
