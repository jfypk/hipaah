"""
Masking utilities for PHI data in HIPAah.

This module provides functions to safely mask sensitive PHI fields in data
structures to ensure HIPAA compliance in logs and user interfaces.
"""

import copy
import re
from typing import Any, Dict, List, Union, Optional, Pattern

# Default mask character sequence
DEFAULT_MASK = "***"

def mask_data(
    data: Any, 
    fields_to_mask: List[str], 
    mask_value: str = DEFAULT_MASK, 
    preserve_type: bool = False
) -> Any:
    """
    Recursively mask specified fields in a data structure.
    
    This function traverses through dictionaries, lists, and other data structures,
    replacing the values of specified fields with a mask value.
    
    Args:
        data: The data structure to mask (can be dict, list, or primitive)
        fields_to_mask: List of field names to mask
        mask_value: The value to use as a mask (default: "***")
        preserve_type: If True, try to preserve the original type (e.g., replace 
                      numbers with 0, booleans with False)
    
    Returns:
        A deep copy of the data with sensitive fields masked
    """
    # Return immediately if no fields to mask or data is None
    if not fields_to_mask or data is None:
        return data
    
    # Handle primitive types
    if not isinstance(data, (dict, list)):
        return data
    
    # Make a deep copy to avoid modifying the original
    masked_data = copy.deepcopy(data)
    
    if isinstance(masked_data, dict):
        for key, value in masked_data.items():
            if key in fields_to_mask:
                # Mask this field
                if preserve_type:
                    # We need to handle booleans first because isinstance(True, int) also returns True in Python
                    if isinstance(value, bool):
                        masked_data[key] = False
                    elif isinstance(value, (int, float)):
                        masked_data[key] = 0
                    elif isinstance(value, str):
                        masked_data[key] = mask_value
                    else:
                        masked_data[key] = mask_value
                else:
                    masked_data[key] = mask_value
            elif isinstance(value, (dict, list)):
                # Recursively mask nested data
                masked_data[key] = mask_data(value, fields_to_mask, mask_value, preserve_type)
    
    elif isinstance(masked_data, list):
        for i, item in enumerate(masked_data):
            masked_data[i] = mask_data(item, fields_to_mask, mask_value, preserve_type)
    
    return masked_data

def mask_phi_patterns(
    text: str, 
    patterns: Optional[List[Union[str, Pattern]]] = None, 
    mask_value: str = DEFAULT_MASK
) -> str:
    """
    Mask PHI patterns in text based on regex patterns.
    
    This is useful for sanitizing free text fields that might contain PHI data
    like SSNs, phone numbers, emails, etc.
    
    Args:
        text: The text to mask
        patterns: List of regex patterns (either compiled patterns or strings)
                 If None, default patterns for common PHI will be used
        mask_value: The value to use as a mask (default: "***")
    
    Returns:
        Text with PHI patterns masked
    """
    if not text:
        return text
    
    # Default PHI patterns if none provided
    if patterns is None:
        patterns = [
            # SSN patterns
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            # Phone number patterns
            r'\b\(\d{3}\)\s*\d{3}[-\s]?\d{4}\b',  # (800) 555-1234 format
            r'\(\d{3}\)\s+\d{3}-\d{4}',           # (800) 555-1234 exact format
            r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',   # 555-123-4567 format
            # Email patterns
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Date patterns (various formats)
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            # Credit card patterns
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            # Medical record numbers (common formats)
            r'\bMRN:?\s*\d{5,10}\b',
            r'\b[A-Z]{2,4}-\d{5,10}\b'
        ]
    
    masked_text = text
    
    for pattern in patterns:
        if isinstance(pattern, str):
            masked_text = re.sub(pattern, mask_value, masked_text)
        else:
            # Assume it's a compiled regex pattern
            masked_text = pattern.sub(mask_value, masked_text)
    
    return masked_text

def mask_fields_except(
    data: Dict[str, Any], 
    allowed_fields: List[str], 
    mask_value: str = DEFAULT_MASK
) -> Dict[str, Any]:
    """
    Mask all fields except those explicitly allowed.
    
    This is the opposite of mask_data - instead of specifying which fields to mask,
    you specify which fields to allow.
    
    Args:
        data: The dictionary to mask
        allowed_fields: List of field names to allow (not mask)
        mask_value: The value to use as a mask (default: "***")
    
    Returns:
        A deep copy of the data with all fields except allowed ones masked
    """
    if not isinstance(data, dict):
        return data
    
    # Get all field names from the data
    all_fields = list(data.keys())
    
    # Calculate fields to mask (all fields except allowed ones)
    fields_to_mask = [field for field in all_fields if field not in allowed_fields]
    
    # Use the regular mask_data function
    return mask_data(data, fields_to_mask, mask_value)

def safe_log_filter(log_data: Dict[str, Any], masked_fields: List[str]) -> Dict[str, Any]:
    """
    Filter and mask sensitive data for safe logging.
    
    This function is specifically designed for logging scenarios, where you want to
    ensure no PHI is accidentally logged.
    
    Args:
        log_data: The data to be logged
        masked_fields: Fields to mask in the data
    
    Returns:
        Filtered and masked data safe for logging
    """
    # Always mask these fields regardless of what's passed
    default_sensitive_fields = [
        "password", "secret", "token", "key", "ssn", "social_security",
        "credit_card", "cc_number", "credential", "auth", "patient_id",
        "mrn", "medical_record_number"
    ]
    
    # Combine with user-provided fields
    all_masked_fields = list(set(masked_fields + default_sensitive_fields))
    
    # Mask the data
    return mask_data(log_data, all_masked_fields)

def redact_json_for_logging(
    data: Dict[str, Any],
    phi_fields: Optional[List[str]] = None,
    max_depth: int = 5,
    max_array_items: int = 3
) -> Dict[str, Any]:
    """
    Redact sensitive data and truncate large structures for efficient logging.
    
    This function not only masks PHI fields but also truncates large arrays
    and deep nested structures to avoid excessive logging.
    
    Args:
        data: The data to redact
        phi_fields: Fields to mask as PHI
        max_depth: Maximum depth to traverse
        max_array_items: Maximum number of items to include from arrays
    
    Returns:
        Redacted data safe and efficient for logging
    """
    if phi_fields is None:
        phi_fields = []
    
    def _redact(value, current_depth=0):
        # Stop at max depth
        if current_depth >= max_depth:
            return "... (truncated due to depth)"
        
        # Handle different types
        if isinstance(value, dict):
            result = {}
            for k, v in value.items():
                # Mask PHI fields
                if k in phi_fields:
                    result[k] = DEFAULT_MASK
                else:
                    result[k] = _redact(v, current_depth + 1)
            return result
                
        elif isinstance(value, list):
            # Truncate long arrays
            if len(value) > max_array_items:
                return [_redact(item, current_depth + 1) for item in value[:max_array_items]] + [f"... ({len(value) - max_array_items} more items)"]
            else:
                return [_redact(item, current_depth + 1) for item in value]
                
        elif isinstance(value, str) and len(value) > 100:
            # Truncate long strings
            return value[:100] + f"... ({len(value) - 100} more chars)"
            
        else:
            return value
    
    return _redact(data)