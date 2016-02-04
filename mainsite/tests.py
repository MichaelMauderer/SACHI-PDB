from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class SignupNotificationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        email = 'test@st-andrews.ac.uk'
        password = '123456'
        post_data = {'username': email,
                     'password1': password,
                     'password2': password,
        }
        response = self.client.post(reverse('requestaccess'), post_data)
        User.objects.get(username=email)

        self.assertEqual(1, len(mail.outbox))

        mail_message = str(mail.outbox[0].message())
        self.assert_(email in mail_message)
