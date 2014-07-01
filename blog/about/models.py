from flask import url_for
from blog import db


class About(db.Document):
    body = db.StringField(required=True)

    def get_absolute_url(self):
        return url_for('about')

    def __unicode__(self):
        return self.body

    meta = {
        'allow_inheritance': True
    }
