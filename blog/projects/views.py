import datetime
import PyRSS2Gen
from flask import Blueprint, render_template, url_for, Response
from flask.views import View, MethodView
from models import Project
import xml.dom.minidom

projects = Blueprint('projects', __name__, template_folder='templates')


class ListView(MethodView):

    def get(self):
        projects = Project.objects.all()
        return render_template('projects/list.html', projects=projects)


class TagView(MethodView):

    def get(self, tag):
        projects = Project.objects(tags=tag)
        return render_template('projects/list.html', projects=projects)


class DetailView(MethodView):

    def get(self, slug):
        project = Project.objects.get_or_404(slug=slug)
        return render_template('projects/detail.html', project=project)


# Register the urls
projects.add_url_rule('/projects/', view_func=ListView.as_view('list'))
projects.add_url_rule('/p/t/<tag>', view_func=TagView.as_view('tags'))
projects.add_url_rule('/p/s/<slug>/', view_func=DetailView.as_view('detail'))
