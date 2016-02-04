from django.db import models
import hashlib
import time
from django.conf import settings
import datetime
from django.core.exceptions import ValidationError


def year_of_birth_validator(value):
    if not (1900 < value < 3000):
        raise ValidationError(u'%s is not a valid year of birth' % value)


class ParticipantManager(models.Manager):

    def get_eligible(self, min_age=None, max_age=None, localy_available=None,
                            genders=None, handedness=None, vision=None):
        """
        Return queryset containing all participants that match the given criteria.
        If a criteria is None (default for all) it will be ignored.

        Keyword arguments:
        min_age -- minimum age of participants as number
        max_age -- maximum age of participants as number
        localy_available -- boolean specifying if participant has to be localy available
        genders -- list of allowed gender values
        handedness -- list of allowed handedness values
        vision -- list of allowed vision values
        """
        participants = Participant.objects.filter(is_activated=True)

        if min_age is not None:
            participants = participants.filter(year_of_birth__lt=datetime.date.today().year - min_age)
        if max_age is not None:
            participants = participants.filter(year_of_birth__gt=datetime.date.today().year - max_age)
        if genders is not None:
            participants = participants.filter(gender__in=genders)
        if handedness is not None:
            participants = participants.filter(handedness__in=handedness)
        if vision is not None:
            participants = participants.filter(vision__in=vision)
        if localy_available is not None and localy_available:
            participants = participants.filter(is_localy_available=True)

        return participants


class Participant(models.Model):
    """
    A Participant is a person that has signed up to be contacted for
    participations in user studies. The given information and the activation
    status of the participant will determine which emails the Participant
    receives.

    # Create some participants
    >>> alice = Participant.objects.create(email="alice@mail.org", gender=Participant.FEMALE, is_activated=True)
    >>> bob = Participant.objects.create(email="bob@mail.org", gender=Participant.MALE, is_activated=True)
    >>> eve = Participant.objects.create(email="eve@mail.org", gender=Participant.FEMALE, is_activated=False)

    # Get email addresses from female participants
    >>> Participant.objects.get_eligible(genders=[Participant.MALE])
    [<Participant: Participant(bob@mail.org)>]

    # Get email addresses from male participants
    >>> Participant.objects.get_eligible(genders=[Participant.FEMALE])
    [<Participant: Participant(alice@mail.org)>]

    """

    objects = ParticipantManager()

    class Meta:
        permissions = (
            ("add_privately", "May add participant using the internal form"),
            ("send_mails_to", "Is allowed to send mails to participants"),
        )

    FEMALE = 0
    MALE = 1

    LEFTHANDED = 10
    RIGHTHANDED = 11
    AMBIDEXTROUS = 12

    NO_CORRECTED_VISION = 20
    GLASSES = 21
    CONTACT_LENSES = 22

    GENDER_CHOICES = ((MALE, 'male'),
                      (FEMALE, 'female')
                      )

    HANDEDNESS_CHOICES = ((LEFTHANDED, 'left handed'),
                  (RIGHTHANDED, 'right handed'),
                  (AMBIDEXTROUS, 'ambidextrous'),
                  )

    VISION_CHOICES = ((NO_CORRECTED_VISION, 'no corrected vision'),
                      (GLASSES, 'glasses'),
                      (CONTACT_LENSES, 'contact lenses')
                      )

    email = models.EmailField(unique=True, blank=False)
    year_of_birth = models.IntegerField(default=19, validators=[year_of_birth_validator])
    gender = models.IntegerField(choices=GENDER_CHOICES, default=FEMALE)
    handedness = models.IntegerField(choices=HANDEDNESS_CHOICES,
                                      default=RIGHTHANDED)
    vision = models.IntegerField(choices=VISION_CHOICES,
                                 default=NO_CORRECTED_VISION)
    is_localy_available = models.BooleanField(default=True)

    is_activated = models.BooleanField(default=False)
    activate_token = models.CharField(max_length=64, unique=True)
    unsubscribe_token = models.CharField(max_length=64, unique=True)

    def save(self, force_insert=False, force_update=False, using=None):

        if not self.activate_token:
            self.activate_token = self.create_token(time.time(), settings.SECRET_KEY[:len(settings.SECRET_KEY) // 2])
        if not self.unsubscribe_token:
            self.unsubscribe_token = self.create_token(time.time(), settings.SECRET_KEY[len(settings.SECRET_KEY) // 2:])

        models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using)

    def create_token(self, *salt_args):
        """
        Return token string generated from feeding the participants email
        address and the given arguments in a sha1 function.
        """
        sha = hashlib.sha1()
        sha.update(self.email)
        for arg in salt_args:
            sha.update(str(arg))
        return sha.hexdigest()

    def __unicode__(self):
        return 'Participant({0})'.format(self.email)
