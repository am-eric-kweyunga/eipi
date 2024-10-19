# loading all the modules
import sys
import click
import yaml
import importlib

from eipi.constants import MODULES
from eipi.errors import EipiParserError, EipiError


def load_modules():
    """Loading the modules configurations from the yml file."""
    try:
        with open("eipi.config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config.get("modules", [])
    except FileNotFoundError:
        # no config file
        return []
    except yaml.YAMLError:
        click.echo(
            click.style("Error: Invalid YAML formatting in config file.", fg="red")
        )
        raise EipiParserError("Invalid YAML formatting.")
    except Exception as e:
        click.echo(
            click.style(
                "An unexpected error occurred while loading the config.", fg="red"
            )
        )
        raise EipiError(f"Unexpected error in loading database config., {e}")


def load_module(module_name):
    """Dynamically load a module by name."""
    try:
        # Assuming modules are structured as 'eipi.modules.module_name'
        module_path = f"eipi.modules.{module_name}"
        module = importlib.import_module(module_path)
        # Call an initialization function if it exists
        if hasattr(module, "initialize"):
            module.initialize()
    except ImportError:
        click.echo(
            click.style(f"Error: Module {module_name} could not be imported.", fg="red")
        )
        sys.exit(1)
    except Exception as e:
        click.echo(
            click.style(f"Error: Failed to load module {module_name}.", fg="red")
        )
        raise EipiError(f"Error loading module {module_name}: {e}")


def use_modules():
    """Collecting all the modules used in the Eipi construction."""
    modules = load_modules()

    # Check if module exists among the registered modules
    for module in modules:
        # Throwing an error if module not found
        if module["use"] not in MODULES:
            click.echo(
                click.style(
                    f"Error: Module '{module["use"]}' is not recognized as a registered Eipi module",
                    fg="red",
                )
            )
            sys.exit(1)

        # Load the module if it is in the registered module list
        load_module(module["use"])
