# validators.py

import click
from flask import jsonify

# Mapping of string-based types to actual Python types
TYPE_MAP = {
    "str": str,
    "int": int,
    "bool": bool,
    "float": float,
    "list": list,
    "dict": dict,
}


def validate_request_data(request_data, expected_data):
    """
    Validate the incoming request data matches the expected data structure.
    Returns None if valid, otherwise a Flask response with error details.

    Args:
        request_data (dict): Incoming JSON payload.
        expected_data (dict): Expected data structure with string-based types.

    Returns:
        Flask Response: If invalid, returns a 400 error with detailed information.
        None: If valid.
    """
    if not isinstance(request_data, dict):
        click.echo(f"Invalid JSON format: {request_data}")
        return jsonify({"error": "Invalid JSON format."}), 400

    # Check for missing and extra keys
    missing_keys = [key for key in expected_data if key not in request_data]
    # extra_keys = [key for key in request_data if key not in expected_data]

    if missing_keys:
        click.echo(f"Missing keys: {missing_keys}")
        return (
            jsonify(
                {
                    "error": "Invalid data structure.",
                    "missing_keys": missing_keys,
                    "suggestion": "Ensure the request contains all required keys and no extra keys.",
                }
            ),
            400,
        )

    # Check for type mismatches
    type_mismatches = []
    mismatch_details = []

    for key, type_str in expected_data.items():
        expected_type = TYPE_MAP.get(type_str)

        if expected_type is None:
            click.echo(f"Unknown type '{type_str}' for key '{key}'")
            return jsonify({"error": f"Unknown type '{type_str}' for key '{key}'"}), 400

        actual_value = request_data.get(key)
        if not isinstance(actual_value, expected_type):
            type_mismatches.append(key)
            mismatch_details.append(
                {
                    "key": key,
                    "expected_type": type_str,
                    "actual_type": type(actual_value).__name__,
                    "suggestion": f"Ensure the value of '{key}' is of type '{type_str}'.",
                }
            )

    if type_mismatches:
        
        # using click to print the error message
        click.echo(f"Type mismatch for one or more fields: {type_mismatches}")
        
        return (
            jsonify(
                {
                    "error": "Type mismatch for one or more fields.",
                    "mismatched_keys": type_mismatches,
                    "details": mismatch_details,
                }
            ),
            400,
        )

    # If everything is valid, return None (no errors)
    return None
