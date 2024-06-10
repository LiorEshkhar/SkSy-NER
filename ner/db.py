import sqlalchemy
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
import click

db = SQLAlchemy()


def get_db():
    if 'db' not in g:
        db_host = "34.159.220.2"
        db_user = "SkSyGruppeE"
        db_pass = "cocacola"
        db_name = "SkSyProject"
        db_port = 3306

        connection = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name,
            ),
            future=True
        ).connect()
        g.db = connection.execution_options(stream_results=True)
    return g.db


def close_db(e=None):
    db_conn = g.pop('db', None)
    if db_conn is not None:
        db_conn.close()


def init_db():
    db_conn = get_db()
    with current_app.open_resource('schema.sql') as f:
        sql_statements = f.read().decode('utf8')
        for statement in sql_statements.split(';'):
            if statement.strip():
                db_conn.execute(sqlalchemy.text(statement))


@click.command('init_db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    db.init_app(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def execute_query(query, params=None):
    db_conn = get_db()
    if params:
        result = db_conn.execute(sqlalchemy.text(query), params)
    else:
        result = db_conn.execute(sqlalchemy.text(query))
    return result
