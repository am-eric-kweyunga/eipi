from flask import jsonify, make_response, Response
import json


def handle_accepted_headers(response_data, request):
    """
    Handle the content type based on the Accept header of the request.
    """
    # Handle the 'Accept' header for outgoing responses
    accept_header = request.headers.get("Accept", "application/json")

    if "application/json" in accept_header or "*/*" in accept_header:
        return jsonify(response_data), 200

    elif "text/html" in accept_header:
        html_response = f"<html><body><pre>{json.dumps(response_data, indent=4)}</pre></body></html>"
        return make_response(html_response, 200, {"Content-Type": "text/html"})

    elif "text/plain" in accept_header:
        text_response = json.dumps(response_data, indent=4)
        return Response(text_response, 200, {"Content-Type": "text/plain"})

    else:
        return (
            jsonify(
                {
                    "error": "Unsupported media type requested.",
                    "supported_types": ["application/json", "text/html", "text/plain"],
                }
            ),
            415,
        )
