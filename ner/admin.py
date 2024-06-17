from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ner.auth import login_required, admin_only
from ner.db import execute_query, get_db

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

@bp.route('/delete_user/<int:id>', methods=["POST"])
@admin_only()
def delete_user(id):
    db = get_db()
    execute_query("DELETE FROM post WHERE author_id = :id", {"id": id})
    execute_query("DELETE FROM user WHERE id = :id", {"id": id})
    db.commit()
    flash("User and all their posts deleted", "success")
    return redirect(url_for('admin.user_overview'))