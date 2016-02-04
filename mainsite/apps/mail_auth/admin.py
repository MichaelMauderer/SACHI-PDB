from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from mainsite.apps.mail_auth.models import send_activation_mail

UserAdmin.actions += [send_activation_mail]