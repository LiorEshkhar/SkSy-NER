from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ner.auth import login_required, admin_only
from ner.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/user_overview')
@admin_only()
def user_overview():
    flash("User overview not implemented yet")
    return redirect(url_for('index'))

@bp.route('/delete_user/<int:id>', methods=["GET", "POST"])
@admin_only()
def delete_user():
    flash("Deleting users was not implemented yet")
    return redirect(url_for('index'))