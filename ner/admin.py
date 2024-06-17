from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from ner.auth import login_required, admin_only
from ner.db import execute_query
bp = Blueprint('admin', __name__, url_prefix='/admin')
@bp.route('/user_overview')
@admin_only()
def user_overview():
    flash("User overview not implemented yet")
    return redirect(url_for('index'))
@bp.route('/delete_user/<int:id>', methods=["GET", "POST"])
@admin_only()
def delete_user(id):
    db = get_db()
    execute_query("DELETE FROM post WHERE user_id = :id", {"id": id})
    execute_query("DELETE FROM user WHERE id = :id", {"id": id})
    db.commit()
    flash("User and all their posts deleted", "success")
    return redirect(url_for('index'))