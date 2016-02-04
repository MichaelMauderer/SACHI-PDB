from django.conf import settings


def add_contact_email(request):
    return {'contact_email': settings.CONTACT_EMAIL}