from flask import Flask
from flask.ext.mako import MakoTemplates, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import json
import logging

config = json.load(open("config/config.json", "r"))

app = Flask(__name__)
mako = MakoTemplates(app)
app.template_folder = "templates"
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("database_uri", None)
db = SQLAlchemy(app)


class BlogPost(db.Model):
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


@app.route("/")
def index():
    return render_template("index.html", blog_posts=BlogPost.query.all())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=8080)
