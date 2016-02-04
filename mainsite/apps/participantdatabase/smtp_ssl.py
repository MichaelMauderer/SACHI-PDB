import smtplib

from django.core.mail.backends import smtp
from django.conf import settings


class EmailBackend(smtp.EmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 fail_silently=False, keyfile=None, certfile=None, **kwargs):
        smtp.EmailBackend.__init__(self, host=host,
                                   port=port,
                                   username=username,
                                   password=password,
                                   use_tls=True,
                                   fail_silently=fail_silently,
        )
        self.keyfile = keyfile or settings.EMAIL_KEYFILE
        self.certfile = certfile or settings.EMAIL_CERTFILE

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            # If local_hostname is not specified, socket.getfqdn() gets used.
            # For performance, we use the cached FQDN for local_hostname.
            self.connection = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls(certfile=self.certfile,
                                         keyfile=self.keyfile)
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise
