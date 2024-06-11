import sqlalchemy
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
import click
# current_app - points to the flask application handling the request
# g (global) - a unique object for each request used to store information over multiple functions 


db = SQLAlchemy()

def get_db():
    """ Returns a connection to the database """
    # if not connected, conntect
    if 'db' not in g:
        g.db = sqlalchemy.create_engine(
            current_app.config['SQLALCHEMY_DATABASE_URI']
            ).connect()
    return g.db


def close_db(e=None):
    """ Close the connection to the database """
    db_conn = g.pop('db', None)

    if db_conn is not None:
        db_conn.close()


def init_db():
    """ Initialise the database as specified in schema.sql """
    db_conn = get_db()
    # open resource opens a file relative to the running package
    with current_app.open_resource('schema.sql') as f:
        sql_statements = f.read().decode('utf8')
        for statement in sql_statements.split(';'):
            if statement.strip():
                db_conn.execute(sqlalchemy.text(statement))


# click is a module that allows creating cli commands
@click.command('init_db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    db.init_app(app)
    # call close_db after returning a response
    app.teardown_appcontext(close_db)
    # add a new command that can be called with the flask command
    # flask --app ner init_db
    app.cli.add_command(init_db_command)


def execute_query(query, params=None):
    db_conn = get_db()
    if params:
        result = db_conn.execute(sqlalchemy.text(query), params)
    else:
        result = db_conn.execute(sqlalchemy.text(query))
    return result
