import os

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'  # change this to a proper location

SECRET_KEY = os.environ.get("SECRET_KEY", None)
