from flask import Flask
from flask.ext.mako import MakoTemplates, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import json
import logging
from kitchen.text.converters import to_unicode

config = json.load(open("config/config.json", "r"))

app = Flask(__name__)
app.config["MAKO_INPUT_ENCODING"] = 'utf-8'
app.config["MAKO_OUTPUT_ENCODING"] = 'utf-8'
app.template_folder = "templates"
mako = MakoTemplates(app)
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
    return render_template("index.html", blog_posts=blog_posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=8080, use_reloader=True)
