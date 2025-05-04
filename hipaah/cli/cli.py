import typer
import json
from pathlib import Path
from hipaah.core.policy_loader import load_policies
from hipaah.core.engine import evaluate_policy
from hipaah.core.types import PolicyRequest
from hipaah.utils.logger import SafeLogger

app = typer.Typer()

@app.command()
def test_policy(
    policy_file: Path = typer.Argument(..., help="Path to policy YAML file"),
    input_file: Path = typer.Argument(..., help="Path to JSON file of resource to evaluate"),
    role: str = typer.Option(..., help="User role"),
    intent: str = typer.Option(..., help="Access intent"),
    attributes: str = typer.Option("{}", help="JSON string of attribute overrides"),
    redact_fields: str = typer.Option("", help="Comma-separated list of fields to redact in logs"),
):
    """Evaluate a policy file against a test input"""
    # Load policies
    policies = load_policies(str(policy_file))

    # Load the resource
    with open(input_file, "r") as f:
        resource = json.load(f)

    # Parse attributes
    attrs = json.loads(attributes)

    # Evaluate
    req = PolicyRequest(role=role, intent=intent, attributes=attrs, resource=resource)
    result = evaluate_policy(req, policies)

    # Masked logging
    fields_to_mask = redact_fields.split(",") if redact_fields else []
    logger = SafeLogger(masked_fields=fields_to_mask)
    logger.info("Access decision", result)


if __name__ == "__main__":
    app()
