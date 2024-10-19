# This function will help to request data depending on the method provided

import click
from flask import request


def request_data_with_method_specification(method):
    methods = ["GET", "POST", "DELETE", "PUT"]
    
    # Ensuring the incoming method is in the methods list
    if method not in methods:
        click.echo(f"Error: Method '{method}' is not supported.")
        return

    try:
        if method == "GET":
            data = request.get_json(silent=True)
            return data
        elif method == "POST" or method == "PUT" or method == "DELETE":
            data = request.get_json()
            print(data)
            return data
    except Exception as e:
        raise e