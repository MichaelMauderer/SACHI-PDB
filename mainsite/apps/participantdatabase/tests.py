from __future__ import unicode_literals
import doctest
import datetime

import mock
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, UserManager, Permission
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings

from models import Participant as p
import models


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(models))
    return tests


class MockDate(datetime.date):
    """
    Class used to mock date.
    """
    @classmethod
    def today(cls):
        return cls(2013, 1, 1)


class ParticipantDBTestCase(TestCase):

    def setUp(self):
        self.anonymous_client = Client()
        self.authorised_client = self.create_authorised_client('tester1', 'tester1@test.com', 'secret')
        self.registered_client = self.create_registered_client('tester', 'tester@test.com', 'verysecret')

    def create_registered_client(self, name, email, password):
        client = Client()
        manager = UserManager()
        manager.model = User
        user = manager.create_user(name, email, password)
        user.save()
        client.login(username=name, password=password)
        return client

    def create_authorised_client(self, name, email, password):
        client = Client()
        manager = UserManager()
        manager.model = User
        user = manager.create_user(name, email, password)
        user.user_permissions.add(Permission.objects.get(codename="send_mails_to"))
        user.user_permissions.add(Permission.objects.get(codename="add_privately"))
        self.assert_(user.has_perm('participantdatabase.send_mails_to'))
        self.assert_(user.has_perm('participantdatabase.add_privately'))
        user.save()
        client.login(username=name, password=password)
        return client


class ParticipantTestCase(TestCase):

    def setUp(self):
        create = p.objects.create
        self.alice = create(email="alice@mail.com", year_of_birth=1970,
                            gender=p.FEMALE, handedness=p.LEFTHANDED,
                            vision=p.NO_CORRECTED_VISION, is_localy_available=True,
                            is_activated=True)
        self.bob = create(email="bob@mail.com", year_of_birth=1994,
                            gender=p.FEMALE, handedness=p.RIGHTHANDED,
                            vision=p.CONTACT_LENSES, is_localy_available=True,
                            is_activated=True)
        self.chris = create(email="chris@mail.com", year_of_birth=1996,
                            gender=p.FEMALE, handedness=p.RIGHTHANDED,
                            vision=p.GLASSES, is_localy_available=False,
                            is_activated=True)
        self.eve = create(email="eve@mail.com", year_of_birth=2000,
                          gender=p.FEMALE, handedness=p.AMBIDEXTROUS,
                          vision=p.NO_CORRECTED_VISION, is_localy_available=True,
                          is_activated=True)
        self.daniel = create(email="daniel@mail.com", year_of_birth=1987,
                             gender=p.FEMALE, handedness=p.RIGHTHANDED,
                             vision=p.NO_CORRECTED_VISION, is_localy_available=True,
                             is_activated=False)

    def test_handedness(self):
        lefthanded_correct = {self.alice}
        righthanded_correct = {self.bob, self.chris}
        ambidextrous_correct = {self.eve}

        self.assertItemsEqual(lefthanded_correct,
                              p.objects.get_eligible(handedness=[p.LEFTHANDED]),
                              )
        self.assertItemsEqual(righthanded_correct,
                              p.objects.get_eligible(handedness=[p.RIGHTHANDED]),
                              )
        self.assertItemsEqual(ambidextrous_correct,
                              p.objects.get_eligible(handedness=[p.AMBIDEXTROUS]),
                              )
        self.assertItemsEqual(lefthanded_correct.union(righthanded_correct),
                              p.objects.get_eligible(handedness=[p.LEFTHANDED, p.RIGHTHANDED]),
                              )
        self.assertItemsEqual(lefthanded_correct.union(righthanded_correct.union(ambidextrous_correct)),
                              p.objects.get_eligible(handedness=[p.LEFTHANDED, p.RIGHTHANDED, p.AMBIDEXTROUS]),
                              )

    @mock.patch('datetime.date', MockDate)
    def test_age(self):
        self.assertItemsEqual({self.bob, self.alice},
                              p.objects.get_eligible(min_age=18),
                              )
        self.assertItemsEqual({self.eve, self.chris},
                              p.objects.get_eligible(max_age=18),
                              )
        self.assertItemsEqual({self.bob},
                              p.objects.get_eligible(min_age=18, max_age=20),
                              )

    def test_vision(self):
        self.assertItemsEqual({self.eve, self.alice},
                              p.objects.get_eligible(vision=[p.NO_CORRECTED_VISION])
                              )
        self.assertItemsEqual({self.eve, self.alice, self.bob},
                              p.objects.get_eligible(vision=[p.NO_CORRECTED_VISION, p.CONTACT_LENSES]),
                              )

    def test_availability(self):
        self.assertItemsEqual({self.alice, self.bob, self.eve},
                              p.objects.get_eligible(localy_available=True),
                              )
        self.assertItemsEqual({self.alice, self.bob, self.chris, self.eve},
                              p.objects.get_eligible(localy_available=False),
                              )


class MailSendingTestCase(ParticipantDBTestCase):

    fixtures = ['mail_test.json']

    def setUp(self):
        ParticipantDBTestCase.setUp(self)
        self.email = "test123211@domain3942872934.com"

    def test_add_participant(self):
        response = self.authorised_client.get(reverse('addparticipant'))
        self.failUnlessEqual(response.status_code, 200)
        email_address = 'test@dummy.org'
        post_data = {'email': 'test@dummy.org',
                     'year_of_birth': '1986',
                     'gender': str(p.MALE),
                     'handedness': str(p.RIGHTHANDED),
                     'vision': str(p.GLASSES),
                     'is_localy_available': 'on'
        }
        response = self.authorised_client.post(reverse('addparticipant'), post_data)
        self.assertEqual(1, len(mail.outbox))
        mail_message = str(mail.outbox[0].message())
        participant = p.objects.get(email=email_address)
        self.assert_(participant.activate_token in mail_message, 'Activate token not found in activation email.')
        self.assert_(participant.unsubscribe_token in mail_message, 'Delete token not found in activation email.')
        self.assert_(settings.CONTACT_EMAIL in mail_message, 'Contact email address not found in activation email.')

    def test_send_message(self):
        mail_text = u"abscdefg76\u2665\xa3\xa3\xa3\xa3\xa3"
        mail_subject = u'Subject2342\xa3'
        post_data = {'genders': [p.MALE],
                     'handedness': [p.LEFTHANDED, p.RIGHTHANDED, p.AMBIDEXTROUS],
                     'vision': [p.NO_CORRECTED_VISION, p.GLASSES, p.CONTACT_LENSES],
                     'is_localy_available': 'off',
                     'message_text': mail_text,
                     'message_subject': mail_subject,
                     'contact_address': self.email,

        }
        self.authorised_client.post(reverse('sendmessage'), post_data)

        #One participant, one admin mail
        self.assertEqual(1 + 1, len(mail.outbox))

        mail_message = mail.outbox[0].message().as_string().decode('utf-8')
        print(mail_message.__class__.__name__)
        self.assert_(mail_subject in mail_message)
        self.assert_(mail_text in mail_message)
        self.assert_(settings.CONTACT_EMAIL in mail_message, 'Contact email address not found in outgoing email.')


class AccessTestCase(ParticipantDBTestCase):

    def assert_access_possible(self, client, url):
        response = client.get(url)
        self.failUnlessEqual(response.status_code, 200)

    def assert_redirect(self, client, url, redirect_target):
        response = client.get(url)
        self.assertRedirects(response, redirect_target)

    def assert_403(self, client, url):
        response = client.get(url)
        self.failUnlessEqual(response.status_code, 403)

    def assert_no_access(self, client, url):
        response = client.get(url)
        self.failIfEqual(response.status_code, 200)

    def test_public_access(self):
        for url in [reverse('addparticipant_public'), reverse('login'), ]:
            self.assert_access_possible(self.authorised_client, url)
            self.assert_access_possible(self.registered_client, url)
            self.assert_access_possible(self.anonymous_client, url)

    def test_restricted_access(self):
        for url in map(reverse, ['sendmessage', 'addparticipant']):
            self.assert_redirect(self.anonymous_client, url, '{0}?next={1}'.format(reverse('login'), url))
            self.assert_no_access(self.registered_client, url)
            self.assert_access_possible(self.authorised_client, url)


class TokenTestCase(TestCase):

    def setUp(self):
        create = p.objects.create
        self.alice = create(email="alice@mail.com")

        self.client = Client()

    def test_acitvation(self):
        self.alice = p.objects.get(pk=self.alice.pk)
        self.assertFalse(self.alice.is_activated)
        response = self.client.get(reverse('activate', kwargs={'token': self.alice.activate_token}))
        self.alice = p.objects.get(pk=self.alice.pk)
        self.failUnlessEqual(response.status_code, 200)
        self.assert_(self.alice.is_activated)

    def test_unsubscribe(self):
        response = self.client.get(reverse('unsubscribe', kwargs={'token': self.alice.unsubscribe_token}))
        self.failUnlessEqual(response.status_code, 200)
        try:
            get_object_or_404(p, pk=self.alice.pk)
            self.assertFalse()
        except Http404:
            pass
