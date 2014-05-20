import datetime
import PyRSS2Gen
from flask import Blueprint, render_template, url_for
from flask.views import View, MethodView
from blog.models import Post
import xml.dom.minidom

posts = Blueprint('posts', __name__, template_folder='templates')


class RobotsView(View):

    def dispatch_request(self):
        return \
            "User-agent: *\n" \
            "Disallow:"


class ListView(MethodView):

    def get(self):
        posts = Post.objects.all()
        return render_template('posts/list.html', posts=posts)


class TagView(MethodView):

    def get(self, tag):
        posts = Post.objects(tags=tag)
        return render_template('posts/list.html', posts=posts)


class DetailView(MethodView):

    def get(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        return render_template('posts/detail.html', post=post)


class RSSView(MethodView):

    def generate_post_rss(self, post):
        desc = str(post.body)[:100]+(
            "..." if (len(str(post.body)) > 100)
            else ""
        )
        return PyRSS2Gen.RSSItem(
            title=post.title,
            link="http://destrock.com"+url_for('posts.detail', slug=post.slug),
            description=desc,
            guid=PyRSS2Gen.Guid(
                "http://destrock.com"+url_for('posts.detail', slug=post.slug)
            ),
            pubDate=post.created_at,
            author="mischa@destrock.com",
            categories=post.tags
        )

    def generate_rss(self, posts):
        rss_items = []
        for post in posts:
            rss_items.append(self.generate_post_rss(post))

        rss = PyRSS2Gen.RSS2(
            title="Mischa Aster Alff's Blog",
            link="http://destrock.com",
            description="Aster's Ramblings, Tips, and Thoughts",
            lastBuildDate=datetime.datetime.utcnow(),
            items=rss_items
        )
        rssxml = xml.dom.minidom.parseString(rss.to_xml())
        return rssxml.toprettyxml()

    def get(self):
        posts = Post.objects.all()
        return self.generate_rss(posts)


# Register the urls
posts.add_url_rule('/', view_func=ListView.as_view('list'))
posts.add_url_rule('/rss', view_func=RSSView.as_view('rss'))
posts.add_url_rule('/t/<tag>', view_func=TagView.as_view('tags'))
posts.add_url_rule('/s/<slug>/', view_func=DetailView.as_view('detail'))
posts.add_url_rule('/robots.txt', view_func=RobotsView.as_view('robots'))
