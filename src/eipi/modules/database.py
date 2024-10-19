import uuid
import click
import yaml
from tinydb import TinyDB, Query
from eipi.errors import DatabaseError, EipiParserError


def load_database_config():
    """Load the database configuration from the YAML file."""
    try:
        with open("eipi.config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config.get("database", None)
    except FileNotFoundError:
        # no database
        return None
    except yaml.YAMLError:
        click.echo(
            click.style("Error: Invalid YAML formatting in config file.", fg="red")
        )
        raise EipiParserError("Invalid YAML formatting.")
    except Exception:
        click.echo(
            click.style(
                "An unexpected error occurred while loading the config.", fg="red"
            )
        )
        raise DatabaseError("Unexpected error in loading database config.")


# Load the database configuration, if available
db_config = load_database_config()
db = None

if db_config:
    try:
        db = TinyDB(
            f"{db_config.get('DATABASE_NAME', 'default_db')}.json",
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )
    except Exception as e:
        click.echo(click.style(f"Database Initialization Error: {str(e)}", fg="red"))
else:
    pass


@click.command()
def fetch_tables():
    """Fetch and list all tables in the database."""
    if not db:
        click.echo(click.style("No database initialized.", fg="yellow"))
        return

    try:
        tables = db.tables()
        if not tables:
            click.echo(click.style("No tables found in the database.", fg="yellow"))
            return

        click.echo(click.style("Tables in the database:", fg="green"))
        for table in tables:
            click.echo(f" - {table}")
    except Exception:
        click.echo(click.style("Error fetching tables from the database.", fg="red"))


@click.command()
@click.option(
    "--table_name", prompt="Enter the table name", help="Name of the table to drop"
)
def drop_table(table_name):
    """Drop a table from the database."""
    if not db:
        click.echo(click.style("No database initialized.", fg="yellow"))
        return

    try:
        if table_name not in db.tables():
            click.echo(click.style(f"Table '{table_name}' not found.", fg="red"))
            return

        db.drop_table(table_name)
        click.echo(
            click.style(f"Table '{table_name}' dropped successfully.", fg="green")
        )
    except Exception:
        click.echo(click.style(f"Error dropping table '{table_name}'.", fg="red"))


def create_table(table_name, columns):
    """Create a table in TinyDB with the provided name and columns."""
    if not db:
        click.echo(click.style("No database initialized.", fg="yellow"))
        return

    try:
        if table_name in db.tables():
            raise DatabaseError(f"Table '{table_name}' already exists.")

        # Create the table and insert a sample document
        table = db.table(table_name)
        sample_doc = {column["name"]: None for column in columns}
        table.insert(sample_doc)

        print(
            f"Table '{table_name}' created with columns: {[col['name'] for col in columns]}."
        )
    except DatabaseError as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {str(e)}", fg="red"))


@click.command()
def list_tables():
    """List all database tables and their fields from the configuration."""
    if not db_config:
        click.echo(click.style("No database configuration found.", fg="yellow"))
        return

    try:
        tables = db_config.get("DATABASE_TABLES", [])

        if not tables:
            click.echo(
                click.style("No tables defined in the configuration.", fg="yellow")
            )
            return

        for table in tables:
            click.echo(click.style(f"Table: {table['name']}", fg="blue"))
            for column in table.get("columns", []):
                col_info = f"{column['name']} ({column['type']})"
                if column.get("primary_key"):
                    col_info += " [Primary Key]"
                if column.get("unique"):
                    col_info += " [Unique]"
                if column.get("nullable") is False:
                    col_info += " [Not Null]"
                click.echo(f" - {col_info}")
    except Exception:
        click.echo(click.style("Error listing tables.", fg="red"))


@click.command()
def init_db():
    """Initialize the database by creating tables from the configuration."""
    if not db_config:
        click.echo(
            click.style(
                "No database configuration found. Skipping initialization.", fg="yellow"
            )
        )
        return

    try:
        tables = db_config.get("DATABASE_TABLES", [])

        if not tables:
            click.echo(
                click.style("No tables defined for initialization.", fg="yellow")
            )
            return

        for table in tables:
            try:
                create_table(table["name"], table.get("columns", []))
                click.echo(
                    click.style(
                        f"Table '{table['name']}' created successfully.", fg="green"
                    )
                )
            except DatabaseError as e:
                click.echo(click.style(f"Error: {str(e)}", fg="red"))
            except Exception as e:
                click.echo(
                    click.style(
                        f"Failed to create table '{table['name']}': {str(e)}", fg="red"
                    )
                )
    except Exception:
        click.echo(click.style("Database initialization failed.", fg="red"))
