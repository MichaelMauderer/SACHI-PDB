from django.forms import ModelForm, Form
from models import Participant
from django.forms.fields import IntegerField, BooleanField,\
    MultipleChoiceField, EmailField, CharField
from django.forms.widgets import CheckboxSelectMultiple, Textarea


class ParticipantForm(ModelForm):
    class Meta:
        model = Participant
        exclude = ('activate_token',
                   'unsubscribe_token',
                   'is_activated')
    is_localy_available = BooleanField(initial=True,
                                       label='Available for experiments in St Andrews'
                                       )


class PublicParticipantForm(ParticipantForm):
    """
    A variant of the ParticipantForm that requires the user to check an 
    additional checkbox, certifying she is okay with the privacy statement.
    """

    privacy_label = "I have read, understand and accept the fair collection statement."
    privacy_error = 'Please read and accept the fair collection statement.'

    accept_privacy_statement = BooleanField(required=True, initial=False,
                                            label=privacy_label,
                                            error_messages={'required': privacy_error})


class ParticipantSearchForm(Form):
    """
    Form asking for all the data needed to collect relevant participants.
    """

    min_age = IntegerField(99, 0, required=False)
    max_age = IntegerField(99, 0, required=False)
    genders = MultipleChoiceField(choices=Participant.GENDER_CHOICES,
                                 widget=CheckboxSelectMultiple,
                                 required=False,
                                 initial=[Participant.MALE, Participant.FEMALE])
    handedness = MultipleChoiceField(choices=Participant.HANDEDNESS_CHOICES,
                                     widget=CheckboxSelectMultiple,
                                     required=False,
                                     initial=[Participant.RIGHTHANDED,
                                              Participant.LEFTHANDED,
                                              Participant.AMBIDEXTROUS])
    vision = MultipleChoiceField(choices=Participant.VISION_CHOICES,
                                 widget=CheckboxSelectMultiple,
                                 required=False,
                                 initial=[Participant.NO_CORRECTED_VISION,
                                          Participant.GLASSES,
                                          Participant.CONTACT_LENSES])
    localy_available = BooleanField(required=False, label="Participant has to attend experiment personally in St Andrews")
    contact_address = EmailField()
    message_subject = CharField()
    message_text = CharField(widget=Textarea)
