from functools import wraps
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ner.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# load the user before each request (not only those handled by the blueprint)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id, )
        ).fetchone()

# define a decorator that redirects the user to the login page if it is not logged in
def login_required(error_msg="Login first to access this part of the site", msg_category="warning"):
    """
    A decorator to require login. If the user is not logged in they will be redirected to the login page and an error message will be flashed. 

    Args:
        error_msg: The error message to be flashed 
        msg_category: The flash category. Warning by default.
    """
    def login_required_decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                flash(error_msg, msg_category)
                return redirect(url_for('auth.login'))

            return view(*args, **kwargs)
        return wrapped_view

    return login_required_decorator

# define a decorator that redirects the user to the login page if it is not logged in
def admin_only(error_msg="Only admins can access this part of the site", msg_category="warning"):
    """
    A decorator to only enable access to admins. If the user is not logged in or not an admin they will be redirected to the login page and an error message will be flashed. 

    Args:
        error_msg: The error message to be flashed 
        msg_category: The flash category. Warning by default.
    """
    def admin_only_decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None or g.user['role'] != "admin":
                flash(error_msg, msg_category)
                return redirect(url_for('index'))

            return view(*args, **kwargs)
        return wrapped_view

    return admin_only_decorator

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
                db.execute(
                    "INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, generate_password_hash(password), "user")
                )
                db.commit()
            except db.IntegrityError:
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
        db = get_db()
        error = None
        # search a user with this username
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        # make sure the user exists and verify the password
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password."
        
        # if verified, "log in", aka save the id to the session
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True # 'remember me' 
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
