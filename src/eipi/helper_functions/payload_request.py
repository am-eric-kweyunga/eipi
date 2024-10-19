import json
import requests
from jinja2 import Template, Environment, select_autoescape
from eipi.errors import EipiParserError, EipiPayloadError

# Initialize Jinja2 environment
env = Environment(autoescape=select_autoescape(["html", "xml"]))

# Constants
VALID_HTTP_METHODS = ["POST", "PUT", "DELETE", "GET"]


def add_payload_route(payload: dict):
    """Send a request based on the provided payload action.

    Args:
        payload (dict): The payload containing action details.

    Raises:
        EipiPayloadError: If the HTTP method is invalid.
        EipiParserError: If an error occurs while handling the payload.

    Returns:
        Response: The response from the HTTP request.
    """
    payload_action = payload["action"]
    if not payload_action:
        raise EipiPayloadError("Missing 'action' in payload.")

    method = payload_action.get("method")
    headers = payload_action.get("headers", {})
    url = payload_action.get("url")

    if method not in VALID_HTTP_METHODS:
        raise EipiPayloadError(f"Invalid HTTP method '{method}' for your payload.")

    try:
        # Render the payload data using Jinja2
        rendered_data = render_payload_data(payload_action)

        # Perform the HTTP request based on the method
        if method == "POST":
            return perform_post_request(url, headers, rendered_data)

        elif method == "GET":
            return perform_get_request(url, headers)

    except requests.RequestException as e:
        log_error(f"Request exception occurred: {e}")
    except Exception as e:
        log_error(f"An unexpected error occurred: {e}")

    raise EipiParserError(f"Can't handle the payload for method '{method}'. check the Error logs file for more details.")


def render_payload_data(payload_action):
    """Render payload data using Jinja2 templates.

    Args:
        payload_action (dict): The action details containing the body.

    Returns:
        dict: The rendered data payload as a dictionary.
    """
    try:
        # Using Jinja2 to render the data payload
        data_template = Template(json.dumps(payload_action.get("body", {})))
        rendered_data = data_template.render(**locals())
        return json.loads(rendered_data)

    except Exception as e:
        log_error(f"Error rendering payload data: {e}")
        raise


def perform_post_request(url, headers, data):
    """Send a POST request.

    Args:
        url (str): The URL to send the request to.
        headers (dict): The headers for the request.
        data (dict): The data payload for the request.

    Returns:
        Response: The response from the POST request.
    """
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
    except Exception as e:
        raise e
    return response


def perform_get_request(url, headers):
    """Send a GET request.

    Args:
        url (str): The URL to send the request to.
        headers (dict): The headers for the request.

    Returns:
        Response: The response from the GET request.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response


def log_error(message):
    """Log error messages to a file.

    Args:
        message (str): The error message to log.
    """
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"Error: {message}\n")
