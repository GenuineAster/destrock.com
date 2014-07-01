import datetime
from flask import url_for
from blog import db


class Project(db.Document):
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True
    )
    title = db.StringField(max_length=255, required=True)
    tags = db.ListField(db.StringField(max_length=30))
    slug = db.StringField(max_length=255, required=True)
    body = db.StringField(required=True)

    def get_absolute_url(self):
        return url_for('project', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }

