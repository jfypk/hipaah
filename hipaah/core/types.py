from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class PolicyRequest:
    role: str
    intent: str
    attributes: Dict[str, Any]
    resource: Dict[str, Any]
