import os
import secrets
from flask import Flask, render_template, request, flash, redirect, url_for

def create_app(test_config=None):
    # create and configure the app
    # paths in config files are realtive to instance folder
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(32),
        DATABASE=os.path.join(app.instance_path, 'ner.sqlite')
    )

    # load further configuration from a config file
    if test_config is None:
        # load the instance config when not testing
        # fail silently if it does not exist
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # set up database 
    from . import db
    db.init_app(app)

    # import and register blueprints
    from . import auth
    from . import posts
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)
    
    # register the endpoint 'index' additionally to posts.index to allow easier access
    app.add_url_rule('/', 'index')

    # custom 404 behavior
    @app.errorhandler(404)
    def page_not_found(e): 
        # If some custom message was sent, display it
        if e.description != "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.":
            error = e.description
        else:
            error = f"The URL {request.path} does not exist"

        flash(error, "error")
        return redirect(url_for('index'))

    # custom 403 behavior
    @app.errorhandler(403)
    def forbidden(e): 
        # If some custom message was sent, display it
        if e.description != "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.":
            error = e.description
        else:
            error = f"You are not allowed to access this resource."

        flash(error, "error")
        return redirect(url_for('index'))

    return app