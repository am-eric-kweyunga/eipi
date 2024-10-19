import os
import click
from dotenv import load_dotenv
from eipi.errors import EipiEnvironmentError

ENV_CONFIG = {}  # Global variable to store env configurations


def load_env_configurations():
    """Loading the env configurations from the .env.eipi file."""
    global ENV_CONFIG
    try:
        if not os.path.exists(".env.eipi"):
            pass
        # Load the env variables from the file
        if load_dotenv(".env.eipi"):
            ENV_CONFIG = {key: os.getenv(key) for key in os.environ.keys()}
        else:
            return None

    except Exception as e:
        click.echo(
            click.style(
                f"An unexpected error occurred while loading the config: {e}", fg="red"
            )
        )

    return ENV_CONFIG


def initialize():
    """Initialize the environment configurations."""
    env_config = load_env_configurations()

    if env_config:
        click.echo(click.style("Loading environment variables...", fg="green"))


def get_env(key: str):
    """Dynamically print the value of a specified environment variable."""
    value = ENV_CONFIG.get(key)
    if value:
        return value
    else:
        return None
