import json
from tinydb import TinyDB, Query
from eipi.errors import DatabaseError
from eipi.modules.database import db
from jinja2 import Environment, select_autoescape, Template

env = Environment(autoescape=select_autoescape(["html", "xml"]))


# getting database actions
def get_database_actions(database_config):
    """Get the database actions from the database configuration."""
    database_actions = database_config.get("actions", [])
    if not database_actions:
        raise ValueError("No database actions found in the configuration.")
    return database_actions


# inserting data into the database
def insert_data(actions, locals):
    """Insert data into the database."""

    for action in actions:
        if action["action"] == "insert":
            table_name = action["table"]
            data = action["data"]

            _data = {field: locals.get(field) for field in action["data"]}

            # Render the data template with the provided _data
            data_template = Template(
                json.dumps(data)
            )  # Convert to JSON string for rendering
            rendered_data = data_template.render(_data)  # Render the template
            response_ = json.loads(
                rendered_data
            )  # Parse the rendered string back to dict

            db.table(table_name).insert(response_)
            print(f"Inserted data '{data}'")
            print(
                f"Inserted data into table '{table_name}' with response '{response_}'."
            )


# updating data in the database
def update_data(actions, locals):
    """Update data in the database."""
    Q = Query()
    for action in actions:
        if action["action"] == "update":
            table_name = action["table"]
            query = action["query"]
            data = action["data"]
            db.table(table_name).update(data, Q.id == query["id"])


# getting data from the database
def select_data(actions, locals):
    """Retrieve data from the database."""
    for action in actions:
        if action["action"] == "select":
            Q = Query()
            table_name = action["table"]
            query_variable = action.get("query_variable", "")

            # Render the data template with the provided _data
            data_template = Template(
                json.dumps(action["query"])
            )  # Convert to JSON string for rendering
            rendered_data = data_template.render(locals)  # Render the template
            response_ = json.loads(
                rendered_data
            )  # Parse the rendered string back to dict

            # Perform the database query
            try:
                # Assuming the rendered query contains the actual value for the field
                result = db.table(table_name).get(Q[query_variable] == response_)

                print(f"Retrieved data from table '{table_name}': {result}")
                return result
            except Exception as e:
                print(f"Error retrieving data: {e}")
                return None
