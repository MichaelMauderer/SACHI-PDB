from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import UserManager
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

# Create your tests here.
from django.test import client
from mainsite.apps.mail_auth import views, models
from mainsite.apps.mail_auth.models import UserAuthToken


class ActivationTest(TestCase):

    def setUp(self):
        self.client = client.Client()

        manager = UserManager()
        manager.model = get_user_model()
        self.user = manager.create_user('mm285', 'mm285@st-andrews.ac.uk', '123456')
        self.user.is_active = False
        self.user.save()
        self.user_auth_token = UserAuthToken(user=self.user)
        self.user_auth_token.save()

    def test_user_activation(self):
        user = get_user_model().objects.get(id=self.user.id)
        self.assertFalse(user.is_active)
        response = self.client.get(reverse(views.activate_view, args=(self.user_auth_token.activate_token,)))
        user = get_user_model().objects.get(id=self.user.id)
        self.assertTrue(user.is_active)

    def test_mail_sending(self):
        factory = client.RequestFactory()
        models.send_activation_mail(UserAdmin, factory.get('/'), get_user_model().objects.all())
        self.assertTrue(len(mail.outbox) == 1)
        mail_message = str(mail.outbox[0].message())
        self.assert_(self.user_auth_token.activate_token in mail_message)
        self.assert_(self.user_auth_token.user.email in mail_message)