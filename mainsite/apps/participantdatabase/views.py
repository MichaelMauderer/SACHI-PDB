from django.shortcuts import render, get_object_or_404, redirect
from django.template.context import Context
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.core.mail import get_connection
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils.html import escape
from django.core import mail

from models import Participant
from forms import ParticipantForm, PublicParticipantForm, ParticipantSearchForm
from decorators import permision_required_or_message


def __plain_text_to_html(text):
    paragraphs = []
    line_buffer = []
    for line in text.splitlines():
        if line:
            line_buffer.append(escape(line))
        else:
            paragraphs.append(u'<br>'.join(line_buffer))
            line_buffer = []
    paragraphs.append(u'<br>'.join(line_buffer))
    template = u'<p>{0}</p>'
    return u'\n'.join([template.format(paragraph) for paragraph in paragraphs])


def unsubscribe_view(request, token):
    participant = get_object_or_404(Participant, unsubscribe_token=token)
    participant.delete()
    return render(request, 'unsubscribe_message.html')


def activate_view(request, token):
    participant = get_object_or_404(Participant, activate_token=token)
    participant.is_activated = True
    participant.save()
    return render(request, 'activate_message.html')


def __add_participant(request, public):
    form_class = PublicParticipantForm if public else ParticipantForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            new_participant = form.save()

            activation_url = reverse('activate', kwargs={'token': new_participant.activate_token})
            activation_url = request.build_absolute_uri(activation_url)

            unsubscribe_url = reverse('unsubscribe', kwargs={'token': new_participant.unsubscribe_token})
            unsubscribe_url = request.build_absolute_uri(unsubscribe_url)

            subject = '{0} Activation mail'.format(settings.MAIL_PREFIX)

            context = Context({'activation_url': activation_url,
                               'unsubscribe_url': unsubscribe_url,
                               'contact_email': settings.CONTACT_EMAIL,
                               'message_title': subject,
            })

            text_mail_template = get_template('emails/activation.txt')
            html_mail_template = get_template('emails/activation.html')

            text_content = text_mail_template.render(context)
            html_content = html_mail_template.render(context)

            connection = get_connection()
            connection.open()
            try:
                email = mail.EmailMultiAlternatives(subject, text_content,
                                                    settings.DEFAULT_FROM_EMAIL,
                                                    [new_participant.email],
                                                    connection=connection,
                )

                email.attach_alternative(html_content, "text/html")
                email.send()
            finally:
                connection.close()

            message = 'Succefsully added {0}. You should now receive a confirmation email to activate your account.'.format(
                new_participant.email)
            messages.add_message(request, messages.SUCCESS, message)

            return redirect('/')
    else:
        form = form_class()

    template = 'add_participant.html' if public else 'add_participant_internal.html'

    return render(request, template, {
        'form': form,
    })


@login_required
@permision_required_or_message('participantdatabase.send_mails_to', '/')
def private_add_participant(request):
    return __add_participant(request, False)


def public_add_participant(request):
    return __add_participant(request, True)


@login_required
@permision_required_or_message('participantdatabase.send_mails_to', '/')
def send_message_view(request):
    if request.method == 'POST':
        form = ParticipantSearchForm(request.POST)
        if form.is_valid():
            subject = u'{0} {1}'.format(settings.MAIL_PREFIX,
                                        form.cleaned_data['message_subject'])
            message = form.cleaned_data['message_text']
            sender = form.cleaned_data['contact_address']

            min_age = form.cleaned_data['min_age']
            max_age = form.cleaned_data['max_age']
            genders = form.cleaned_data['genders']
            handedness = form.cleaned_data['handedness']
            vision = form.cleaned_data['vision']
            localy_available = form.cleaned_data['localy_available']

            recipients = Participant.objects.get_eligible(min_age, max_age,
                                                          localy_available,
                                                          genders, handedness,
                                                          vision)

            text_mail_template = get_template('emails/experiment_invitation.txt')
            html_mail_template = get_template('emails/experiment_invitation.html')

            connection = get_connection()
            connection.open()
            try:
                for recipient in recipients:
                    unsubscribe_url = reverse('unsubscribe', kwargs={'token': recipient.unsubscribe_token})
                    unsubscribe_url = request.build_absolute_uri(unsubscribe_url)

                    text_context = Context({'message': message,
                                            'unsubscribe_url': unsubscribe_url,
                                            'contact_email': settings.CONTACT_EMAIL,
                                            'message_title': subject,
                    })
                    html_context = Context({'message': __plain_text_to_html(message),
                                            'unsubscribe_url': unsubscribe_url,
                                            'contact_email': settings.CONTACT_EMAIL,
                                            'message_title': subject,
                    })

                    text_content = text_mail_template.render(text_context)
                    html_content = html_mail_template.render(html_context)

                    email = mail.EmailMultiAlternatives(subject, text_content,
                                                        settings.DEFAULT_FROM_EMAIL,
                                                        [recipient.email],
                                                        headers={'Reply-To': sender})
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                if recipients:
                    email = mail.EmailMultiAlternatives(subject, text_content,
                                                        settings.DEFAULT_FROM_EMAIL,
                                                        [settings.CONTACT_EMAIL],
                                                        headers={'Reply-To': sender})
                    email.attach_alternative(html_content, "text/html")
                    email.send()

            finally:
                connection.close()
            number_of_mails = len(recipients)
            message = ' {0} mails were sent.'.format(number_of_mails)
            messages.add_message(request, messages.SUCCESS, message)
            return redirect('sendmessage')
            #return render(request, 'info_message.html', {'message': message})
    else:
        form = ParticipantSearchForm()

    return render(request, 'send_message.html', {
        'form': form,
    })
