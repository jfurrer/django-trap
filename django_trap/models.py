# This file comes from admin_honeypot by Derek Payton (MIT license).
# See https://github.com/dmpayton/django-admin-honeypot
from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    from django.db.models import GenericIPAddressField
except ImportError:
    from django.db.models import IPAddressField as GenericIPAddressField


class LoginAttempt(models.Model):
    username = models.CharField(_("username"), max_length=255, blank=True, null=True)
    password = models.CharField(_("password"), max_length=255, blank=True, null=True)
    ip_address = GenericIPAddressField(_("ip address"), blank=True, null=True)
    session_key = models.CharField(_("session key"), max_length=50, blank=True, null=True)
    user_agent = models.TextField(_("user-agent"), blank=True, null=True)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    path = models.TextField(_("path"), blank=True, null=True)

    class Meta:
        verbose_name = _("login attempt")
        verbose_name_plural = _("login attempts")
        ordering = ('timestamp',)

    def __str__(self):
        return self.username
