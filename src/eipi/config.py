import click
import yaml
import pathlib
import sys
from eipi.errors import EipiConfigError

BASE_DIR = pathlib.Path(__file__).cwd()
CONFIG_FILE = next(
    (
        path
        for path in [BASE_DIR / "eipi.config.yaml", BASE_DIR / "eipi.config.yml"]
        if path.exists()
    ),
    None,
)

# Reserved words that cannot be used as App names
RESERVED_WORDS = {"eipi", "admin", "config", "settings", "root"}


def load_config():
    """Load and return the configuration from the YAML file."""
    try:
        # Check if the config file exists
        if not CONFIG_FILE:
            raise FileNotFoundError("Configuration file not found.")

        # Load the YAML configuration
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file)
            return config

    except FileNotFoundError:
        click.echo(
            click.style(
                "Error: Could not find the configuration file. "
                "Please ensure it exists in the project directory by running 'eipi init'.",
                fg="red",
            )
        )
        sys.exit(1)

    except yaml.YAMLError:
        click.echo(
            click.style(
                "Error: There was an issue reading the configuration file. "
                "Please ensure it is properly formatted.",
                fg="red",
            )
        )
        sys.exit(1)

    except Exception:
        click.echo(
            click.style(
                "An unexpected error occurred. Please try again later.", fg="red"
            )
        )
        sys.exit(1)
