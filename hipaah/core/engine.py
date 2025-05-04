MASKED = "***"

def evaluate(resource: dict, role: str, intent: str, attributes: dict, policies: list) -> dict:
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
            elif key in policy.allow:
                result[key] = value
        return result

    # Default deny-all
    return {}
