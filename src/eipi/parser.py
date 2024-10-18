import json
import os
import re
from typing import List
from eipi.config import CONFIG_FILE, load_config
from eipi.errors import EipiConfigError, EipiParserError


class Eipi:
    def __init__(self):
        # Load configuration and set up the parser
        self.config = self._load_config()
        self.parser = EipiParser(self.config)

    def _load_config(self):
        """Load and return the configuration from the YAML file."""
        config = load_config()
        return config

    def parse(self):
        """Parse the routes using the EipiParser."""
        try:
            self.parser.parse()
        except EipiParserError as e:
            raise

    def validate(self):
        """Validate the routes using the EipiParser."""
        try:
            routes = self.parser.get_routes()
            for route in routes:
                self.parser.validate_route(route=route)
        except EipiParserError as e:
            raise

    def run(self):
        """Run the application."""
        try:
            self.parser.parse()  # Parse routes
            self.validate()  # Validate routes
            routes = self.parser.get_routes()
            self._initialize_routes(routes)

        except EipiConfigError as e:
            print(f"Configuration error: {e}")
        except EipiParserError as e:
            print(f"Parsing error: {e}")

    def _initialize_routes(self, routes: List[dict]):
        """Initialize the routes (stub for demonstration)."""
        for route in routes:
            print(
                f"Initializing route: {route['name']} at {route['route']} with method {route['method']}"
            )


class EipiParser:
    def __init__(self, config):
        self.config = config
        self.filepath = self._resolve_filepath()
        self.routes = []
        self.validated_routes = []

        if not CONFIG_FILE:
            raise EipiConfigError(
                "Config file not found. Please initialize the Eipi Application by running:\n\n  eipi init"
            )

    def _resolve_filepath(self) -> str:
        """Resolve the correct file path with .eipi or .ei extension."""
        filepath = self.config["root"]
        if os.path.exists(filepath):
            return filepath

        # Check for the same filename with either .eipi or .ei extension
        for ext in [".eipi", ".ei"]:
            alt_path = filepath + ext
            if os.path.exists(alt_path):
                return alt_path

        raise EipiParserError(f"File not found: {filepath}")

    def _remove_comments(self, content: str) -> str:
        """Remove comments from the content, ignoring those inside strings."""

        def replacer(match):
            # Only replace if the match is outside of a string
            return match.group(1) if match.group(1) else ""

        # Regex pattern to capture comments outside of strings
        single_line_comment_pattern = r'("(?:\\.|[^"\\])*")|//.*?$'
        multi_line_comment_pattern = r'("(?:\\.|[^"\\])*")|/\*.*?\*/'

        # Remove single-line comments
        content = re.sub(
            single_line_comment_pattern, replacer, content, flags=re.MULTILINE
        )
        # Remove multi-line comments
        content = re.sub(multi_line_comment_pattern, replacer, content, flags=re.DOTALL)

        return content.strip()

    def validate_route(self, route: dict):
        """Validate a route's structure and content."""
        required_keys = ["name", "route", "method", "response"]

        # Check for required keys
        for key in required_keys:
            if key not in route:
                raise EipiParserError(
                    f"Missing key '{key}' in route '{route.get('name', 'unknown')}'"
                )

        # Validate HTTP method
        if route["method"] not in ["GET", "POST", "PUT", "DELETE"]:
            raise EipiParserError(
                f"Invalid HTTP method '{route['method']}' in route '{route['name']}'"
            )

        # Validate response structure
        if "status" not in route["response"]:
            raise EipiParserError(
                f"Missing 'status' in response for route '{route['name']}'"
            )

        # Validate route format
        if not route["route"].startswith("/"):
            raise EipiParserError(f"Route '{route['name']}' should start with a slash.")

    def parse(self):
        """Parse the provided .eipi or .ei file."""
        try:
            with open(self.filepath, "r") as f:
                raw_data = f.read()

            # Remove comments from the raw data before parsing JSON
            cleaned_data = self._remove_comments(raw_data)

            # Parse the cleaned data
            data = json.loads(cleaned_data)

            if not isinstance(data, list):
                raise EipiParserError("Invalid format. Expected a list of routes.")

            for index, route in enumerate(data):
                try:
                    self.validate_route(route)  # Validate the current route
                    self.routes.append(route)  # Append validated route
                    self.validated_routes.append(route)  # Append validated route
                    if index == 0:
                        self.validated_routes.pop(
                            0
                        )  # Forget the first route after validation
                except EipiParserError as e:
                    raise  # Stop execution on validation error

        except json.JSONDecodeError as e:
            raise EipiParserError(f"Error parsing JSON: {e}")
        except FileNotFoundError:
            raise EipiParserError(f"File not found: {self.filepath}")

    def get_routes(self) -> List[dict]:
        """Return the parsed routes."""

        return self.routes
