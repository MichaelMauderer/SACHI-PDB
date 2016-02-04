from django.conf import settings
from django.template.context import Context
from django.template.loader import get_template
from django.views.generic.edit import CreateView
from django.core import mail

from mainsite.forms import CustomUserCreationForm


class UserCreate(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'user_signup.html'
    success_url = '/login'

    def form_valid(self, form):
        user = form.data['username']
        template = get_template('emails/signup_notification.txt')

        context = Context({'user': user})
        email = mail.EmailMultiAlternatives('[PDB] New user', template.render(context),
                                            settings.DEFAULT_FROM_EMAIL,
                                            [settings.CONTACT_EMAIL],
        )
        email.send()

        return super(UserCreate, self).form_valid(form)