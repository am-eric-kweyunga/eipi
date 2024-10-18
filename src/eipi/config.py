import yaml
import os
import pathlib
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
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)
