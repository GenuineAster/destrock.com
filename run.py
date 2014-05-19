import sys
sys._stdout = sys.stdout
sys.stdout = sys.stderr

import flask
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import json
import logging
from kitchen.text.converters import to_unicode
import hashlib
import re
import os


config = json.load(open("config/config.json", "r"))

app = Flask(__name__)
app.secret_key = config.get(
    "secret_key",
    "Why aren't you using a secret key, Mr Gorski?"  # hue puns
)

app.template_folder = "templates"
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("database_uri", None)
db = SQLAlchemy(app)


class BlogPosts(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    title = db.Column(
        db.String(128)
    )

    function_type = db.Column(
        db.String(128)
    )

    function_name = db.Column(
        db.String(128)
    )

    tags = db.Column(
        db.String(256)
    )

    link_to_content = db.Column(
        db.String(128),
        unique=True
    )

    return_value = db.Column(
        db.String(64)
    )

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.title = kwargs.get("title", None)
        self.function_type = kwargs.get("function_type", None)
        self.function_name = kwargs.get("function_name", None)
        self.tags = kwargs.get("tags", None)
        self.link_to_content = kwargs.get("link_to_content", None)
        self.return_value = kwargs.get("return_value", None)


class Users(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    username = db.Column(
        db.String(64)
    )

    password = db.Column(
        db.String(32)
    )

    def __init__(self, username, password):
        self.username = username
        self.password = password


db.create_all()


class Post(object):
    id = None
    title = None
    function_type = None
    function_name = None
    tags = None
    content = None
    return_value = None

    def __init__(self, db_post):
        self.id = db_post.id
        self.title = db_post.title
        self.function_type = db_post.function_type
        self.function_name = db_post.function_name
        self.tags = db_post.tags
        self.content = to_unicode(
            open(
                "posts/%s" % db_post.link_to_content
            ).read()
        )
        self.return_value = db_post.return_value


@app.route("/")
def index():
    blog_posts = []
    for post in BlogPosts.query.all():
        blog_posts.append(
            to_unicode(render_template("blog_post.html", post=Post(post)))
        )
    return render_template("index.html", blog_posts=reversed(blog_posts))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if "logged_in" not in flask.session:
        if flask.request.method == 'POST':
            username = flask.request.form["username"]
            password = hashlib.md5(flask.request.form["password"]).hexdigest()

            if not username or not password:
                return flask.redirect("/login")

            if Users(username, password) in Users.query.all():
                flask.session["logged_in"] = True
                flask.session.permanent = True
            else:
                flask.session["logged_in"] = False
                return flask.redirect("/login")

            return flask.redirect("/")
        else:
            return render_template("login_form.html")
    else:
        return flask.redirect("/")


@app.route("/logout")
def logout():
    flask.session.pop("logged_in", None)
    return flask.redirect("/")


@app.route("/post", methods=['GET', 'POST'])
def post():
    if "logged_in" not in flask.session:
        return flask.redirect("/login")

    if flask.request.method == 'POST':
        title = flask.escape(flask.request.form["title"])
        function_type = flask.escape(flask.request.form["function_type"])
        function_name = flask.escape(flask.request.form["function_name"])
        tags = flask.escape(flask.request.form["tags"])
        content = flask.request.form["content"]
        return_value = flask.escape(flask.request.form["return_value"])

        filename = re.sub("[^a-z0-9]+", "", title)
        filename = filename.lower()

        while os.path.isfile("posts/" + filename):
            filename += "_"

        f = open("posts/" + filename, "w")
        f.write(content)
        f.flush()
        f.close()

        db.session.add(BlogPosts(
            title=title, function_type=function_type,
            function_name=function_name, tags=tags,
            link_to_content=filename, return_value=return_value
        ))
        db.session.commit()

        return flask.redirect("/")
    else:
        return render_template("new_post.html")

application = app

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=8080, use_reloader=True)
