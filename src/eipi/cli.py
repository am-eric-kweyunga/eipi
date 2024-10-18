import json
import os
import click
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from jinja2 import Template, Environment, select_autoescape

from eipi.config import BASE_DIR, RESERVED_WORDS, load_config
from eipi.modules.database import drop_table, fetch_tables, init_db, list_tables
from eipi.modules.helper import (
    get_database_actions,
    insert_data,
    select_data,
    update_data,
)
from eipi.templates.yaml_file import config_template
from eipi.templates.root_file import root_file_template
from eipi.errors import EipiConfigError, EipiParserError
from eipi.parser import Eipi

# Initialize Jinja2 environment
env = Environment(autoescape=select_autoescape(["html", "xml"]))


def add_payload_route(payload):
    """Create a handler function for a specific route."""
    payload_action = payload["action"]
    method = payload_action["method"]

    if method not in ["POST", "PUT", "DELETE", "GET"]:
        raise EipiParserError(f"Invalid HTTP method for your payload '{method}''")

    try:
        if method == "POST":
            headers = payload_action.get("headers", None)
            
            print(locals())
            
            # Using Jinja2 to render the data payload
            data_template = Template(json.dumps(payload_action["body"]))
            rendered_data = data_template.render(**locals())
            response_ = json.loads(rendered_data)
            
            response = requests.post(
                url=payload_action.get("url", ""),
                headers=headers,
                data=response_,
            )
            return response

        elif method == "GET":
            response = requests.get(
                url=payload_action["url"],
                headers=payload_action["headers"],
            )
            return response

    except requests.RequestException as e:
        # Log errors to a file
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error: {e}\n")

    raise EipiParserError(f"Can't handle the payload '{payload_action['method']}''")


def validate_project_name(value):
    """Validate that the app name is not a reserved word."""
    if value.lower() in RESERVED_WORDS:
        raise click.BadParameter(
            f"'{value}' is a reserved word. Please choose a different app name."
        )
    return value.lower()


# CLI command group
@click.group()
def cli():
    """API Builder CLI for managing .eipi files and APIs."""
    pass


@cli.command()
def init():
    """Initialize a new Eipi Application."""

    config_file_path = os.path.join(BASE_DIR, "eipi.config.yaml")

    if os.path.exists(config_file_path):
        click.echo(click.style("Eipi Project already initialized", fg="green"))
        return

    click.echo(click.style("Welcome to Eipi Project Initialization", fg="green"))

    project_name = click.prompt(
        "Enter your app name",
        type=str,
        default="myapp",
        show_default=True,
        value_proc=validate_project_name,
    )
    root_file = click.prompt(
        "Enter the root file (e.g., api.eipi)",
        type=str,
        default="api.eipi",
        show_default=True,
    )
    description = click.prompt(
        "Enter a brief description of the project",
        type=str,
        default="",
        show_default=False,
    )
    host = click.prompt("Enter the host", default="127.0.0.1", show_default=True)
    port = click.prompt("Enter the port", default=5000, show_default=True, type=int)

    # Create a Jinja2 template
    template = Template(config_template)

    # Render the template with the user's input
    rendered_config = template.render(
        name=project_name, description=description, root=root_file, host=host, port=port
    )

    root_template = Template(root_file_template)

    # Rendering the root file with user's input
    rendered_root_file = root_template.render(name=root_file)

    # Save the rendered config to the YAML file
    with open(config_file_path, "w") as file:
        file.write(rendered_config)

    if os.path.exists(BASE_DIR / "eipi.config.yaml"):
        """Making the root file"""
        with open(BASE_DIR / root_file, "w") as file:
            file.write(rendered_root_file)

    click.echo(
        click.style(f"App '{project_name}' initialized successfully!", fg="blue")
    )
    click.echo(click.style(f"Configuration saved at: {config_file_path}", fg="yellow"))


@cli.command()
def validate():
    """Validate the given .eipi file."""
    eipi = Eipi()
    try:
        eipi.parse()
        eipi.validate()  # Use the Eipi class for validation

    except EipiParserError as e:
        click.echo(click.style(f"Validation failed: {e}", fg="red"))


@cli.command()
def show():
    """Display the routes from the .eipi file."""
    eipi = Eipi()

    try:
        eipi.parse()  # Use the Eipi class for parsing
        routes = eipi.parser.get_routes()
        click.echo(click.style("Parsed Routes:", fg="blue"))
        for route in routes:
            click.echo(
                {
                    "Name": route["name"],
                    "Route": route["route"],
                    "Method": route["method"],
                }
            )
    except EipiParserError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))


@cli.command()
def run():
    """Run the API server using the given .eipi file."""
    # Load configuration from the YAML file
    config = load_config()

    # config variables
    eipi = config.get("eipi", {})
    _config = config.get("config", {})
    cors_enabled = eipi.get("CORS_ENABLED", False)
    allowed_origins = eipi.get("ALLOWED_ORIGINS", [])
    log_level = eipi.get("LOG_LEVEL", "INFO")

    secret_key = _config.get("SECRET_KEY", "your_secret_key")

    # Create a Flask app instance
    app = Flask(__name__)
    app.secret_key = f"{secret_key}"

    # Enable CORS if enabled in the configuration
    if cors_enabled:
        CORS(app, resources={r"/*": {"origins": allowed_origins}})

    host = eipi.get("host", "127.0.0.1")
    port = eipi.get("port", 5000)

    eipi = Eipi()

    try:
        eipi.parse()  # Use the Eipi class for parsing
        routes = eipi.parser.get_routes()

        app.logger.setLevel(log_level)

        def create_handler(route):
            """Create a new handler function for each route."""

            #################################################################
            ## Variables from the parsed route
            #################################################################

            method = route["method"]
            response_template_str = json.dumps(route["response"])
            response = route["response"]
            payload = route.get("payload", None)

            use_database = route.get("use_database", False)
            database = route.get("database", {})

            #################################################################

            # Create a handler function for each route
            def handler():
                log_entry = {
                    "route": route["route"],
                    "method": method,
                    "data": None,
                    "payload_response": None,
                }

                request_data = request.get_json()  # Get the request data
                log_entry["data"] = request_data  # Log the request data

                expected_data = route.get("expected_data", None)
                variables = {}

                if expected_data:
                    variables = {
                        key: request_data.get(value)
                        for key, value in expected_data.items()
                    }
                    locals().update(variables)

                if method == "POST":
                    if payload:
                        if "body" in payload["action"]:
                            payload_body_template = Template(
                                json.dumps(payload["action"]["body"])
                            )
                            payload_body = payload_body_template.render(**variables)
                            payload["action"]["body"] = json.loads(payload_body)

                        res = add_payload_route(payload)  # Make API call with the payload
                        if res:
                            print(res)
                            payload_response = res.json()

                            # Extract variables from payload response if defined
                            response_variables = payload.get("response_variables", {})
                            extracted_values = {
                                key: payload_response.get(path, None)
                                for key, path in response_variables.items()
                            }

                            # Update local variables with extracted values for further processing
                            locals().update(
                                extracted_values
                            )  # Include response variables in locals

                            # Render the response template with the updated variables
                            response_template = Template(response_template_str)
                            response_body = response_template.render(
                                **locals()
                            )  # Render response with all locals
                            response_ = json.loads(
                                response_body
                            )  # Convert the rendered string back to a dictionary
                            response.update(response_)

                            # Update the main response object
                            log_entry["payload_response"] = extracted_values
                        else:
                            app.logger.error("Failed to process payload.")
                            response_ = {"error": "Failed to process payload."}

                    # Log the complete log entry
                    app.logger.info(f"Request Log: {json.dumps(log_entry, indent=4)}")

                if use_database:

                    actions = get_database_actions(database_config=database)
                    for action in actions:
                        if action["action"] not in [
                            "select",
                            "update",
                            "insert",
                            "delete",
                        ]:
                            raise ValueError(
                                f"Invalid database action: {action}. Allowed actions are: create, update, get, delete."
                            )
                        for action in actions:
                            if action["action"] == "select":
                                # selection action
                                res = select_data(actions=actions, locals=locals())
                                locals().update(res)
                            elif action["action"] == "update":
                                # update action
                                update_data(actions=actions, locals=locals())

                            elif action["action"] == "insert":
                                # insert action
                                insert_data(actions=actions, locals=locals())
                            # elif action == "delete":
                            #     delete action
                            #     res = delete_data(actions=actions)
                            else:
                                raise ValueError(
                                    f"Invalid database action: {action}. Allowed actions are: create, update, get, delete."
                                )

                return jsonify(response), response.get("status", 200)

            return handler

        # Register routes with their handlers
        for route in routes:
            if route["method"] not in ["GET", "POST", "PUT", "DELETE"]:
                raise EipiParserError(
                    f"Invalid HTTP method '{route['method']}' in route '{route['name']}'"
                )

            # Create a fresh handler for each route
            handler = create_handler(route)
            endpoint = f"{route['method']}_{route['route']}".replace("/", "_")
            app.add_url_rule(
                route["route"],
                methods=[route["method"]],
                view_func=handler,
                endpoint=endpoint,
            )

        click.echo(click.style(f"Starting server on http://{host}:{port}", fg="green"))

        app.run(host=host, port=port, debug=True)

    except EipiParserError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))


# database commands
cli.add_command(list_tables)
cli.add_command(init_db)
cli.add_command(fetch_tables)
cli.add_command(drop_table)

# Entry point for the CLI
if __name__ == "__main__":
    cli()
