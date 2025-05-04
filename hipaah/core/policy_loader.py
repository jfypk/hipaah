import yaml
from typing import List, Dict, Any

class Policy:
    def __init__(self, role: str, intent: str, allow: List[str], mask: List[str], deny: List[str], conditions: Dict[str, Any] = None):
        self.role = role
        self.intent = intent
        self.allow = set(allow)
        self.mask = set(mask)
        self.deny = set(deny)
        self.conditions = conditions or {}

def load_policies(path: str) -> List[Policy]:
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
            conditions=rule.get("conditions", {})
        ))
    return policies
