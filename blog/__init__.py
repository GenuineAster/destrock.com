import sys
sys._stdout = sys.stdout
sys.stdout = sys.stderr

from flask import Flask
from flask.ext.mongoengine import MongoEngine
import logging
import json
import markdown2

settings = json.loads(open("config/config.json").read())

app = Flask(__name__)
app.template_folder = "templates"
app.config["MONGODB_SETTINGS"] = {'DB': "destrock"}
app.config["SECRET_KEY"] = settings.get("secret_key", "SuPeRsECrEt")
app.config['PROPAGATE_EXCEPTIONS'] = True
db = MongoEngine(app)
application = app


@app.template_filter('markdown')
def markdown_filter(s):
    return markdown2.markdown(
        s, extras={
            "fenced-code-blocks": "",
            "html-classes": {"img": "post_image"}
        }
    )


def register_blueprints(app):
    from blog.admin.views import admin
    from blog.projects.views import projects
    from blog.posts.views import posts
    from blog.contact.views import contact
    from blog.about.views import about
    app.register_blueprint(admin)
    app.register_blueprint(projects)
    app.register_blueprint(posts)
    app.register_blueprint(contact)
    app.register_blueprint(about)

register_blueprints(app)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=5000, use_reloader=True)
