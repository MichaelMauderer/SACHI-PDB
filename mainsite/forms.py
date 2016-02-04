from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import ugettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    username = forms.RegexField(label=_("Email address"), max_length=30,
        regex=r'^[\w.+-]+@st-andrews.ac.uk$',
        help_text=_("Required. Please enter a valid University of St Andrews email address"),
        error_messages={
            'invalid': _("Invalid e-mail address.")})

    def save(self, commit=True):
        user = UserCreationForm.save(self, commit=False)
        user.email = user.username
        if commit:
            user.save()
        return user
