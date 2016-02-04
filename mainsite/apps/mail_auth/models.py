import hashlib
import time

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template.context import Context
from django.template.loader import get_template

from views import activate_view


class UserAuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    activate_token = models.CharField(max_length=64, unique=True)

    def create_token(self, *salt_args):
        """
        Return token string.
        """
        sha = hashlib.sha1()
        sha.update(self.user.email)
        for arg in salt_args:
            sha.update(str(arg))
        return sha.hexdigest()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.activate_token:
            self.activate_token = self.create_token(time.time(), settings.SECRET_KEY[:len(settings.SECRET_KEY) // 2])
        models.Model.save(self,
                          force_insert=force_insert,
                          force_update=force_update,
                          using=using,
                          update_fields=update_fields)


def send_activation_mail(modeladmin, request, queryset):
    for user in queryset:
        user_auth_token, created = UserAuthToken.objects.get_or_create(user=user)
        user_auth_token.save()

        activation_url = reverse(activate_view, kwargs={'token': user_auth_token.activate_token})
        activation_url = request.build_absolute_uri(activation_url)

        subject = '{0} Activation mail'.format(settings.MAIL_PREFIX)

        context = Context({'activation_url': activation_url,
                           'contact_email': settings.CONTACT_EMAIL,
                           'message_title': subject,
        })

        text_mail_template = get_template('mail_auth/emails/activation.txt')
        html_mail_template = get_template('mail_auth/emails/activation.html')

        text_content = text_mail_template.render(context)
        html_content = html_mail_template.render(context)

        email = mail.EmailMultiAlternatives(subject, text_content,
                                            settings.DEFAULT_FROM_EMAIL,
                                            [user.email],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()


send_activation_mail.short_description = 'Send authentication email to user'