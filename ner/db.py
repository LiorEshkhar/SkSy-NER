import sqlite3
import click
from flask import current_app, g
# current_app - points to the flask application handling the request
# g (global) - a unique object for each request used to store information over multiple functions 

# Returns a connection to the database
def get_db():
    # if not connected, conntect
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            # convert sql types to python types using declared types in the schema
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # Return rows that behave like dicts
        g.db.row_factory = sqlite3.Row
    return g.db

# close the connection to the database
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# initalise the database as specified in schema.sql
def init_db():
    db = get_db()

    # open resource - opens a file relative to the running package
    with current_app.open_resource('schema.sql') as s:
        db.executescript(s.read().decode('utf8'))

# click is a module that allows creating cli commands
@click.command('init_db')
def init_db_command():
    """Clear the existing data and create new tables."""

    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    # call close_db after returning a response
    app.teardown_appcontext(close_db)
    # add a new command that can be called with the flask command
    # flask --app ner init_db
    app.cli.add_command(init_db_command)