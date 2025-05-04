from hipaah.core.engine import evaluate_policy
from hipaah.core.policy_loader import load_policies
from hipaah.core.types import PolicyRequest
from hipaah.utils.logger import SafeLogger
from hipaah.clients import HipaahClient, ApiClient
from hipaah.utils import (
    load_resource_from_file,
    save_resource_to_file,
    mask_phi_fields,
    merge_policies
)

__version__ = "0.1.0"

# Create proper public exports
__all__ = [
    "evaluate_policy",
    "load_policies",
    "PolicyRequest",
    "SafeLogger",
    "HipaahClient",
    "ApiClient",
    "load_resource_from_file",
    "save_resource_to_file",
    "mask_phi_fields",
    "merge_policies",
]
