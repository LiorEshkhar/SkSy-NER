from functools import wraps
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from ner.db import get_db, execute_query

bp = Blueprint('auth', __name__, url_prefix='/auth')

ROLES = ["user", "admin"]

# load the user before each request (not only those handled by the blueprint)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = execute_query(
            "SELECT * FROM user WHERE id = :id", {"id": user_id}
        ).fetchone()

# create a decorator generator for decorators that accept the defined roles
def generate_login_required_decorator_generator(error_msg, redirect_endpoint, msg_category="warning", roles=ROLES):
    """
    A function to generate login-decorator generators 

    Args:
        error_msg: The default error message of the decorator generator to be created
        msg_category: The default flash category of the decorator generator to be created. Warning by default.
    """

    def login_required_decorator_generator(error_msg=error_msg, msg_category=msg_category):
        f"""
        A decorator generator to verify users are logged in and are in the allowed roles. If the user is not logged in they will be redirected to {redirect_endpoint} and an error message will be flashed. 

        Args:
            error_msg: The error message to be flashed 
            msg_category: The flash category. Warning by default.
        """

        def login_required_decorator(view):
            @wraps(view)
            def wrapped_view(*args, **kwargs):
                if g.user is None or g.user.role not in roles:
                    flash(error_msg, msg_category)
                    return redirect(url_for(redirect_endpoint))

                return view(*args, **kwargs)

            return wrapped_view

        return login_required_decorator
    return login_required_decorator_generator

login_required = generate_login_required_decorator_generator(error_msg="Login first to access this part of the site", redirect_endpoint='auth.login')
admin_only = generate_login_required_decorator_generator(error_msg="Only admins can access this part of the site", redirect_endpoint='index', roles=["admin"])


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get data
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        # if something something missing, update error
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # if nothing missing, register the user
        if error is None:
            try:
                execute_query(
                    "INSERT INTO user (username, password, role) VALUES (:username, :password, :role)",
                    {"username": username, "password": generate_password_hash(password), "role": "user"}
                )
                db.commit()
            except IntegrityError:
                error = f"User {username} is already registered."
            else:
                flash("Registered successfully", "success")
                return redirect(url_for("auth.login"))

        # if there was an error, flash it
        flash(error, 'error')

    # if it is a GET request or register not successful, return the register page
    return render_template('auth/login_and_register.html', action="Register")


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get posted data
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        # search a user with this username
        user = execute_query(
            "SELECT * FROM user WHERE username = :username", {"username": username}
        ).fetchone()

        # make sure the user exists and verify the password
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        # if verified, "log in", aka save the id to the session
        if error is None:
            session.clear()
            session['user_id'] = user.id
            session.permanent = True  # 'remember me'
            flash("Login successful", "success")
            return redirect(url_for('index'))

        # if there was an error, flash it
        flash(error, 'error')

    # if it is a GET request or login not successful, return the login page
    return render_template('auth/login_and_register.html', action="Login")


@bp.route('/logout')
@login_required("You must be logged in to log out", "info")
def logout():
    # clear all saved information
    session.clear()
    flash("Log out successful", "success")
    return redirect(url_for('index'))
