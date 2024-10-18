root_file_template = """// {{ name }} is an intrance of your Eipi Application.
// This is a starter template for your Eipi application.

/*
 * @starter template
 *
 * File structure:
 *
 * - [] this is the main App instance is initialized using the list
 *
 * - [
 * -    {}, this is the first API dictionary
 * -    {} this is the second API dictionary
 * - ]
 *
 */
 
[
    {
        "name": "API 1",
        "description": "API 1 description",
        "method": "POST",
        "route": "/api1",
        "response": {
            "status": 200,
            "data": {
                "text": "My first API eendpoint using Eipi"
            }
        }
    },
    {
        "name": "API 2",
        "description": "API 2 description",
        "method": "GET",
        "route": "/api2",
        "response": {
            "status": 200,
            "data": {
                "text": "My second API eendpoint using Eipi"
            }
        }
    }
]
"""