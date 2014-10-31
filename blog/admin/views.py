import markdown2

from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView

from flask.ext.mongoengine.wtf import model_form

from auth import requires_auth
from blog.posts.models import Post
from blog.projects.models import Project
from blog.contact.models import Contact
from blog.about.models import About

admin = Blueprint('admin', __name__, template_folder='templates')


class List(MethodView):
    decorators = [requires_auth]
    post_cls = Post
    project_cls = Project

    def get(self):
        posts = self.post_cls.objects.all()
        projects = self.project_cls.objects.all()
        return render_template(
            'admin/list.html', posts=posts, projects=projects
        )


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


class ContactDetail(MethodView):

    decorators = [requires_auth]

    def get_context(self):
        form_cls = model_form(Contact)

        contact = Contact.objects.first()
        if contact:
            if request.method == 'POST':
                form = form_cls(request.form, inital=contact._data)
            else:
                form = form_cls(obj=contact)
        else:
            contact = Contact()
            form = form_cls(request.form)

        context = {
            "contact": contact,
            "form": form,
            "create": False
        }
        return context

    def get(self):
        context = self.get_context()
        return render_template('admin/contact/detail.html', **context)

    def post(self):
        context = self.get_context()
        form = context.get('form')

        if form.validate():
            contact = context.get('contact')
            form.populate_obj(contact)
            contact.save()

            return redirect(url_for('admin.index'))
        return render_template('admin/contact/detail.html', **context)


class AboutDetail(MethodView):

    decorators = [requires_auth]

    def get_context(self):
        form_cls = model_form(About)

        about = About.objects.first()
        if about:
            if request.method == 'POST':
                form = form_cls(request.form, inital=about._data)
            else:
                form = form_cls(obj=about)
        else:
            about = About()
            form = form_cls(request.form)

        context = {
            "about": about,
            "form": form,
            "create": False
        }
        return context

    def get(self):
        context = self.get_context()
        return render_template('admin/about/detail.html', **context)

    def post(self):
        context = self.get_context()
        form = context.get('form')

        if form.validate():
            about = context.get('about')
            form.populate_obj(about)
            about.save()

            return redirect(url_for('admin.index'))
        return render_template('admin/about/detail.html', **context)


class MarkdownPreview(MethodView):
    decorators = [requires_auth]
    def post(self):
        a = markdown2.markdown(
            request.get_data(), extras={
                "fenced-code-blocks": "",
                "html-classes": {"img": "post_image"}
            }
        )

        print a
        print request.get_data()
        return a


# Register the urls
admin.add_url_rule(
    '/admin/', view_func=List.as_view('index')
)
admin.add_url_rule(
    '/admin/post/create/', defaults={'slug': None},
    view_func=PostDetail.as_view('create_post')
)
admin.add_url_rule(
    '/admin/post/<slug>/', view_func=PostDetail.as_view('edit_post')
)
admin.add_url_rule(
    '/admin/project/create/', defaults={'slug': None},
    view_func=ProjectDetail.as_view('create_project')
)
admin.add_url_rule(
    '/admin/project/<slug>/', view_func=ProjectDetail.as_view('edit_project')
)
admin.add_url_rule(
    '/admin/contact/', view_func=ContactDetail.as_view('edit_contact')
)

admin.add_url_rule(
    '/admin/about/', view_func=AboutDetail.as_view('edit_about')
)

admin.add_url_rule(
    '/markdown', view_func=MarkdownPreview.as_view('markdown')
)
