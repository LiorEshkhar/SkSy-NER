from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ner.auth import login_required, admin_only
from ner.db import execute_query

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/user_overview')
@admin_only()
def user_overview():
    users = execute_query(
        "SELECT *\
            FROM user\
            WHERE user.id != :admin_id\
            ORDER BY created DESC",
        {"admin_id": g.user.id}
    ).fetchall()
    return render_template("admin/user_overview.html", users = users)

@bp.route('/delete_user/<int:id>', methods=["GET", "POST"])
@admin_only()
def delete_user():
    flash("Deleting users was not implemented yet")
    return redirect(url_for('index'))