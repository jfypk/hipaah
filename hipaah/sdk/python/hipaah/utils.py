import json
from hipaah.utils.mask import mask_data

def load_resource_from_file(file_path):
    """Load a resource from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The loaded resource
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def save_resource_to_file(resource, file_path):
    """Save a resource to a JSON file.
    
    Args:
        resource: The resource to save
        file_path: Path to save the JSON file
    """
    with open(file_path, 'w') as f:
        json.dump(resource, f, indent=2)

def mask_phi_fields(data, fields_to_mask):
    """Mask PHI fields in data.
    
    Args:
        data: The data containing PHI fields
        fields_to_mask: List of field names to mask
        
    Returns:
        A copy of the data with PHI fields masked
    """
    return mask_data(data, fields_to_mask)

def merge_policies(policy_files):
    """Merge multiple policy files into one.
    
    Args:
        policy_files: List of policy file paths
        
    Returns:
        A merged policy dictionary
    """
    from hipaah.core.policy_loader import load_policies
    
    merged = {}
    for file_path in policy_files:
        policies = load_policies(file_path)
        merged.update(policies)
    
    return merged