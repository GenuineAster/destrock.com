from flask import Blueprint, render_template
from flask.views import MethodView
from models import About

about = Blueprint('about', __name__, template_folder='templates')


class AboutView(MethodView):

    def get(self):
        about = About.objects.first()
        if not about:
            About(
                body="Oops, I haven't defined the about information yet. :("
            ).save()
            about = About.objects.first()
        return render_template('about/index.html', about=about)


# Register the urls
about.add_url_rule('/about/', view_func=AboutView.as_view('index'))
