import json
import os
import click
from flask import Flask, jsonify, request
from flask_cors import CORS
from jinja2 import Template, Environment, select_autoescape

from eipi.config import BASE_DIR, load_config
from eipi.helper_functions.payload_request import add_payload_route
from eipi.helper_functions.request_data import request_data_with_method_specification

from eipi.modules.database import drop_table, fetch_tables, init_db
from eipi.helpers.module_database_helper import get_database_actions, insert_data, select_data, update_data
from eipi.templates.yaml_file import config_template
from eipi.templates.root_file import root_file_template
from eipi.errors import EipiParserError
from eipi.parser import Eipi
from eipi.validators.headers import handle_accepted_headers
from eipi.validators.requests import validate_request_data
from eipi.validators.validate_inputs import validate_project_name

# Initialize Jinja2 environment
env = Environment(autoescape=select_autoescape(["html", "xml"]))

# CLI command group for Eipi
@click.group()
def cli():
    """API Builder CLI for managing .eipi files and APIs."""
    pass


@cli.group()
def app():
    """Manage Eipi Applications."""
    pass


@app.command()
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


@app.command()
def validate():
    """Validate the given .eipi file."""
    eipi = Eipi()
    try:
        eipi.parse()
        eipi.validate()  # Use the Eipi class for validation

    except EipiParserError as e:
        click.echo(click.style(f"Validation failed: {e}", fg="red"))


@app.command()
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


@app.command()
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

    # More configuration for the flask app
    app.secret_key = f"{secret_key}"
    app.json.sort_keys = False

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
            """Create a handler function for each route."""

            # Extract route details
            method = route["method"]
            response_template_str = json.dumps(route["response"])
            use_database = route.get("use_database", False)
            database = route.get("database", {})
            expected_data = route.get("expected_data", None)

            # payload
            payload = route.get("payload", None)

            def handler():
                """Handle incoming requests."""
                # Initialize log entry
                log_entry = {
                    "route": route["route"],
                    "method": method,
                    "data": None,
                    "payload_response": None,
                }

                # Retrieve and validate request data
                request_data = request_data_with_method_specification(method)
                log_entry["data"] = request_data

                # Handle expected data if provided
                if expected_data:
                    # Validate request data using the external function
                    validation_error = validate_request_data(
                        request_data, expected_data
                    )
                    if validation_error:
                        return validation_error  # Return the error response if validation fails

                    # Prepare variables from the expected data
                    variables = (
                        {
                            key: request_data.get(value)
                            for key, value in expected_data.items()
                        }
                        if expected_data
                        else {}
                    )
                    locals().update(variables)

                # Handle database actions if provided
                if use_database:
                    actions = get_database_actions(database_config=database)
                    for action in actions:
                        if action["action"] == "select":
                            res = select_data(actions=actions, locals=locals())
                            locals().update(res)
                        elif action["action"] == "update":
                            update_data(actions=actions, locals=locals())
                        elif action["action"] == "insert":
                            insert_data(actions=actions, locals=locals())
                        else:
                            raise ValueError(
                                f"Invalid database action: {action}. "
                                "Allowed actions are: select, update, insert."
                            )

                # Handling payloads if provided
                if payload:
                    # Process payload actions
                    payload_action = payload.get("action", None)
                    
                    # if the payload action is defined, then we can return the response or error
                    if "body" in payload_action:
                        payload_body_template = Template(
                            json.dumps(payload_action.get("body", {}, None))
                        )
                        payload_body = payload_body_template.render(**variables)
                        payload_action["body"] = json.loads(payload_body)

                # Process POST requests with payloads
                if method == "POST" and payload:
                    # making the internal API call using the payload
                    res = add_payload_route(payload)

                    # if the internal API call is done, then we can return the response or error
                    if res:
                        payload_response = res.json()
                        log_entry["payload_response"] = payload_response

                        # Extract and update variables from the payload response
                        response_variables = payload.get("response_variables", {})
                        extracted_values = {
                            key: payload_response.get(path, None)
                            for key, path in response_variables.items()
                        }
                        locals().update(extracted_values)

                    else:
                        app.logger.error("Failed to process payload.")
                        return jsonify({"error": "Failed to process payload."}), 500

                    # Render the response template with updated variables
                    response_template = Template(response_template_str)
                    response_body = response_template.render(**locals())
                    response_ = json.loads(response_body)
                    route["response"].update(response_)

                    if payload.get("append_to_response") == True:
                        route["response"].update(res.json())

                # Process GET requests
                elif method == "GET":
                    # If payload is provided, make the internal API call
                    if payload:
                        res = add_payload_route(payload)

                        # If the internal API call is done, update the outer response
                        if res:
                            log_entry["payload_response"] = res.json()

                            # Append internal API call response to the outer response if specified
                            if payload.get("append_to_response", None) == "True":
                                incoming_data = res.json()
                                route["response"].update({
                                    "request_data": {
                                        "data": incoming_data
                                    }
                                })

                    if response_template_str:
                        response_template = Template(response_template_str)
                        response_body = response_template.render(**locals())
                        response_ = json.loads(response_body)
                        route["response"].update(response_)

                    # Handling accepted headers
                    return handle_accepted_headers(
                        response_data=route["response"], request=request
                    )

                # Log the request and return the response
                app.logger.info(f"Request Log: {json.dumps(log_entry, indent=4)}")
                return jsonify(route["response"]), route["response"].get("status", 200)

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
            headers = route.get("headers", {})

            # after_request decorator to set response headers
            @app.after_request
            def set_reponse_headers(response):
                response.headers.update(headers)
                return response

            # Register the route with the Flask app
            app.add_url_rule(
                route["route"],
                methods=[route["method"]],
                view_func=handler,
                endpoint=endpoint,
            )

        click.echo(click.style(f"API health check...", fg="green"))
        app.run(host=host, port=port, debug=True)

    except EipiParserError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))


@cli.group()
def database():
    """Eipi Database Operations."""
    pass


@database.command()
def initdb():
    """Initialize the database."""
    click.echo("Initializing the database...")
    init_db()


@database.command()
def dropdb():
    """Drop the database."""
    click.echo("Dropping the database...")
    drop_table()


@database.command()
def showtables():
    """Show tables in the database."""
    tables = fetch_tables()
    click.echo("Tables in the database:")
    for table in tables:
        click.echo(f"- {table}")


# Entry point for the CLI
if __name__ == "__main__":
    cli()
