import datetime
import PyRSS2Gen
from flask import Blueprint, render_template, url_for, Response
from flask.views import View, MethodView
from models import Post
import xml.dom.minidom

posts = Blueprint('posts', __name__, template_folder='templates')


class RSS2(PyRSS2Gen.RSS2):
    def publish(self, handler):
        handler.startElement("rss", self.rss_attrs)
        handler.startElement("channel", self.element_attrs)
        PyRSS2Gen._element(handler, "title", self.title)
        PyRSS2Gen._element(handler, "link", self.link)
        PyRSS2Gen._element(handler, "description", self.description)

        self.publish_extensions(handler)

        PyRSS2Gen._opt_element(handler, "language", self.language)
        PyRSS2Gen._opt_element(handler, "copyright", self.copyright)
        PyRSS2Gen._opt_element(handler, "managingEditor", self.managingEditor)
        PyRSS2Gen._opt_element(handler, "webMaster", self.webMaster)

        pubDate = self.pubDate
        if isinstance(pubDate, datetime.datetime):
            pubDate = PyRSS2Gen.DateElement("pubDate", pubDate)
        PyRSS2Gen._opt_element(handler, "pubDate", pubDate)

        lastBuildDate = self.lastBuildDate
        if isinstance(lastBuildDate, datetime.datetime):
            lastBuildDate = PyRSS2Gen.DateElement(
                "lastBuildDate", lastBuildDate
            )
        PyRSS2Gen._opt_element(handler, "lastBuildDate", lastBuildDate)

        for category in self.categories:
            if isinstance(category, basestring):
                category = PyRSS2Gen.Category(category)
            category.publish(handler)

        PyRSS2Gen._opt_element(handler, "generator", self.generator)
        PyRSS2Gen._opt_element(handler, "docs", self.docs)

        handler.startElement(
            "atom:link",
            {
                "href": "http://destrock.com/rss",
                "rel": "self",
                "type": "application/rss+xml"
            }
        )
        handler.endElement("atom:link")

        if self.cloud is not None:
            self.cloud.publish(handler)

        ttl = self.ttl
        if isinstance(self.ttl, int):
            ttl = PyRSS2Gen.IntElement("ttl", ttl)
        PyRSS2Gen._opt_element(handler, "ttl", ttl)

        if self.image is not None:
            self.image.publish(handler)

        PyRSS2Gen._opt_element(handler, "rating", self.rating)
        if self.textInput is not None:
            self.textInput.publish(handler)
        if self.skipHours is not None:
            self.skipHours.publish(handler)
        if self.skipDays is not None:
            self.skipDays.publish(handler)

        for item in self.items:
            item.publish(handler)

        handler.endElement("channel")
        handler.endElement("rss")


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
            author="mischa@destrock.com ( Mischa Alff )",
            categories=post.tags
        )

    def generate_rss(self, posts):
        rss_items = []
        for post in posts:
            rss_items.append(self.generate_post_rss(post))

        rss = RSS2(
            title="Mischa Aster Alff's Blog",
            link="http://destrock.com",
            description="Aster's Ramblings, Tips, and Thoughts",
            lastBuildDate=datetime.datetime.utcnow(),
            items=rss_items
        )
        rss.rss_attrs['xmlns:atom'] = "http://www.w3.org/2005/Atom"
        rssxml = xml.dom.minidom.parseString(rss.to_xml())
        return rssxml.toprettyxml()

    def get(self):
        posts = Post.objects.all()
        return Response(
            self.generate_rss(posts),
            mimetype="application/rss+xml"
        )


# Register the urls
posts.add_url_rule('/', view_func=ListView.as_view('list'))
posts.add_url_rule('/rss', view_func=RSSView.as_view('rss'))
posts.add_url_rule('/b/t/<tag>', view_func=TagView.as_view('tags'))
posts.add_url_rule('/t/<tag>', view_func=TagView.as_view('compat_tags'))
posts.add_url_rule('/b/s/<slug>/', view_func=DetailView.as_view('detail'))
posts.add_url_rule('/s/<slug>/', view_func=DetailView.as_view('compat_slug'))
posts.add_url_rule('/robots.txt', view_func=RobotsView.as_view('robots'))
