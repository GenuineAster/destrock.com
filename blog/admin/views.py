from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView

from flask.ext.mongoengine.wtf import model_form

from auth import requires_auth
from blog.posts.models import Post
from blog.projects.models import Project

admin = Blueprint('admin', __name__, template_folder='templates')


class List(MethodView):
    decorators = [requires_auth]
    post_cls = Post
    project_cls = Project

    def get(self):
        posts = self.post_cls.objects.all()
        projects = self.project_cls.objects.all()
        return render_template('admin/list.html', posts=posts, projects=projects)


class PostDetail(MethodView):

    decorators = [requires_auth]

    def get_context(self, slug=None):
        form_cls = model_form(Post, exclude=('created_at', 'comments'))

        if slug:
            post = Post.objects.get_or_404(slug=slug)
            if request.method == 'POST':
                form = form_cls(request.form, inital=post._data)
            else:
                form = form_cls(obj=post)
        else:
            post = Post()
            form = form_cls(request.form)

        context = {
            "post": post,
            "form": form,
            "create": slug is None
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('admin/post/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            post = context.get('post')
            form.populate_obj(post)
            tags = request.form['tags'].split(",")
            tags = [tag.strip() for tag in tags]
            post.tags = tags
            post.save()

            return redirect(url_for('admin.index'))
        return render_template('admin/post/detail.html', **context)



class ProjectDetail(MethodView):

    decorators = [requires_auth]

    def get_context(self, slug=None):
        form_cls = model_form(Project, exclude=('created_at', 'comments'))

        if slug:
            project = Project.objects.get_or_404(slug=slug)
            if request.method == 'POST':
                form = form_cls(request.form, inital=project._data)
            else:
                form = form_cls(obj=project)
        else:
            project = Project()
            form = form_cls(request.form)

        context = {
            "project": project,
            "form": form,
            "create": slug is None
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('admin/project/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            project = context.get('project')
            form.populate_obj(project)
            tags = request.form['tags'].split(",")
            tags = [tag.strip() for tag in tags]
            project.tags = tags
            project.save()

            return redirect(url_for('admin.index'))
        return render_template('admin/project/detail.html', **context)


# Register the urls
admin.add_url_rule('/admin/', view_func=List.as_view('index'))
admin.add_url_rule('/admin/post/create/', defaults={'slug': None},
                   view_func=PostDetail.as_view('create_post'))
admin.add_url_rule('/admin/post/<slug>/', view_func=PostDetail.as_view('edit_post'))
admin.add_url_rule('/admin/project/create/', defaults={'slug': None},
                   view_func=ProjectDetail.as_view('create_project'))
admin.add_url_rule('/admin/project/<slug>/', view_func=ProjectDetail.as_view('edit_project'))
