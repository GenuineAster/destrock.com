from flask import Blueprint, render_template
from flask.views import MethodView
from models import Contact

contact = Blueprint('contact', __name__, template_folder='templates')


class ContactView(MethodView):

    def get(self):
        contact = Contact.objects.first()
        if not contact:
        	Contact(
        		body="Oops, I haven't defined the contact information yet. :("
        	).save()
        	contact = Contact.objects.first()
        return render_template('contact/index.html', contact=contact)


# Register the urls
contact.add_url_rule('/contact/', view_func=ContactView.as_view('index'))
