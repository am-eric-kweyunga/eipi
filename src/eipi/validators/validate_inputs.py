import click
from eipi.config import RESERVED_WORDS


def validate_project_name(value):
    """Validate that the app name is not a reserved word."""
    if value.lower() in RESERVED_WORDS:
        raise click.BadParameter(
            f"'{value}' is a reserved word. Please choose a different app name."
        )
    return value.lower()
