from django.core.mail.backends import smtp
from django.conf import settings
import smtplib
from django.core.mail.utils import DNS_NAME


class EmailBackend(smtp.EmailBackend):

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
            self.connection = smtplib.SMTP(self.host, self.port,
                                           local_hostname=DNS_NAME.get_fqdn())
            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls(settings.EMAIL_KEYFILE,
                                         settings.EMAIL_CERTFILE)
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise