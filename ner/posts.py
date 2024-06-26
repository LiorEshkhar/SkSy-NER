from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import spacy
from spacy import displacy
import en_core_web_sm
from ner.auth import login_required, admin_only
from ner.db import get_db, execute_query

bp = Blueprint('posts', __name__)


# Display all public posts
@bp.route('/')
def index():
    posts = execute_query(
        "SELECT p.id, title, body, analysed_body, p.created as created, public, author_id, username\
            FROM post p JOIN user u ON p.author_id = u.id \
            WHERE p.public = TRUE\
            ORDER BY created DESC"
    ).fetchall()
    return render_template('posts/index.html', posts=posts, title="Named Entity Recognition")


@bp.route('/myposts')
@login_required("Log in to view your posts")
def myposts():
    posts = execute_query(
        "SELECT p.id, title, body, analysed_body, p.created as created, public, author_id, username\
            FROM post p JOIN user u ON p.author_id = u.id \
            WHERE author_id = :author_id\
            ORDER BY created DESC",
        {"author_id": g.user.id}
    ).fetchall()
    return render_template('posts/index.html', posts=posts, title=f"{g.user.username.capitalize()}'s Posts")


@bp.route('/create', methods=["GET", "POST"])
@login_required("You must be logged in to create a post")
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        public = request.form.get('public')
        # SQLite does not support true Boolean, but 0 and 1 for F and T
        public = 0 if not public or public != "on" else 1
        error = None

        if not title:
            error = "Title is required."

        if not body:
            error = "Body is required."

        if error is None:
            db = get_db()
            execute_query(
                "INSERT INTO post (title, body, analysed_body, author_id, public)\
                    VALUES (:title, :body, :analysed_body, :author_id, :public)",
                {"title": title, "body": body, "analysed_body": spacy_analysis(body), "author_id": g.user.id, "public": public}
            )
            db.commit()
            flash("Post created", "success")
            return redirect(url_for('posts.myposts'))

        flash(error)

    return render_template('posts/create_and_update.html', action="Create", post=None, url=url_for('posts.myposts'))


def get_post(id, check_author=True):
    # get the post with the requested ID
    post = execute_query(
        "SELECT p.id, title, body, p.created, public, author_id, username\
            FROM post p JOIN user u ON p.author_id = u.id\
            WHERE p.id = :id",
        {"id": id}
    ).fetchone()

    # make sure the post exists
    if post is None:
        abort(404, f"Post not found")

    # make sure the post belongs to the user
    if check_author and post.author_id != g.user.id:
        abort(403, f"You can only edit your own posts")

    return post


@bp.route('/update/<int:id>?url', methods=["GET", "POST"])
@login_required("You can only edit your own posts", "error")
def update(id):
    # Get url to redirect to after the post was updated
    url = request.args.get('url')
    if url is None: url = url_for('index')

    if request.method == "POST":
        title = request.form.get('title')
        body = request.form.get('body')
        public = request.form.get('public')
        public = 0 if not public or public != "on" else 1
        error = None

        if not title:
            error = "Title is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            execute_query(
                "UPDATE post SET title = :title, body = :body, analysed_body = :analysed_body, public = :public WHERE id = :id",
                {"title": title, "body": body, "analysed_body": spacy_analysis(body), "public": public, "id": id}
            )
            db.commit()
            flash("Post updated", "success")
            return redirect(url)

    post = get_post(id)
    print(url)
    return render_template('posts/create_and_update.html', action="Update", post=post, url=url)


@bp.route('/delete/<int:id>?url', methods=["POST"])
@login_required("You can only delete your own posts", "error")
def delete(id):
    get_post(id, check_author = not g.user.role == "admin")
    url = request.args.get('url')
    url = url if url else url_for('index')
    db = get_db()
    execute_query("DELETE FROM post WHERE id = :id", {"id": id})
    db.commit()
    flash("Post deleted", "success")
    return redirect(url)


def spacy_analysis(body):
    """
    Returns the analysed version of body, rendered as HTML
    """
    nlp = en_core_web_sm.load()                              # load language model
    doc = nlp(body)                                          # process input text
    html = displacy.render(doc, style="ent", jupyter=False)  # generate html code

    return html