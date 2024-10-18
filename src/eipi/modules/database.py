import uuid
import click
import yaml
from tinydb import TinyDB, Query, where

from eipi.errors import DatabaseError


def load_database_config():
    """Load the database configuration from the YAML file."""
    with open("eipi.config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config.get("database", {})


db_config = load_database_config()
db = TinyDB(
    f"{db_config.get("DATABASE_NAME")}.json",
    sort_keys=True,
    indent=4,
    separators=(",", ": "),
)


@click.command()
def fetch_tables():
    """Fetch and list all tables in the database."""
    tables = db.tables()

    if not tables:
        click.echo(click.style("No tables found in the database.", fg="yellow"))
        return

    click.echo(click.style("Tables in the database:", fg="green"))
    for table in tables:
        click.echo(f" - {table}")


@click.command()
@click.option(
    "--table_name", prompt="Enter the table name", help="Name of the table to drop"
)
def drop_table(table_name):
    """
    Drop a table from the database.

    """
    table = db.table(table_name)
    if not table:
        click.echo(click.style(f"Table '{table_name}' not found.", fg="red"))
        return

    db.drop_table(table_name)
    click.echo(click.style(f"Table '{table_name}' dropped successfully.", fg="green"))


def create_table(table_name, columns):
    """
    Create a table in TinyDB based on the provided table name and column definitions.

    :param table_name: Name of the table to be created.
    :param columns: A list of dictionaries defining the columns.
    """
    # Check if the table already exists
    if table_name in db.tables():
        raise DatabaseError(f"Table '{table_name}' already exists.")
        return

    # Create a new table with the specified columns
    table = db.table(table_name)

    # Define a document structure based on columns
    sample_doc = {
        column["name"]: None for column in columns
    }  # Set default values as None
    table.insert(sample_doc)  # Insert a sample document to initialize the table

    print(
        f"Table '{table_name}' created with columns: {[column['name'] for column in columns]}."
    )

@click.command()
def list_tables():
    """List all database tables and their fields."""
    tables = db_config.get("DATABASE_TABLES", [])

    if not tables:
        click.echo(
            click.style("No tables found in the database configuration.", fg="yellow")
        )
        return

    for table in tables:
        click.echo(click.style(f"Table: {table['name']}", fg="blue"))
        columns = table.get("columns", [])
        for column in columns:
            col_info = f"{column['name']} ({column['type']})"
            if column.get("primary_key"):
                col_info += " [Primary Key]"
            if column.get("unique"):
                col_info += " [Unique]"
            if column.get("nullable") is False:
                col_info += " [Not Null]"
            click.echo(f" - {col_info}")


@click.command()
def init_db():
    """Initialize the database by creating tables based on the configuration."""
    tables = db_config.get("DATABASE_TABLES", [])

    if not tables:
        click.echo(click.style("No tables defined for initialization.", fg="yellow"))
        return

    for table in tables:
        table_name = table["name"]
        columns = table.get("columns", [])

        # You can call a function to create the table
        try:
            create_table(
                table_name, columns
            )  # Replace with your actual table creation logic
            click.echo(
                click.style(f"Table '{table_name}' created successfully.", fg="green")
            )
        except Exception as e:
            click.echo(
                click.style(f"Failed to create table '{table_name}': {e}", fg="red")
            )
