# This file comes from admin_honeypot by Derek Payton (MIT license).
# See https://github.com/dmpayton/django-admin-honeypot
import django
from django.conf import settings
from django_trap.forms import HoneypotLoginForm
from django_trap.models import LoginAttempt
from django_trap.signals import honeypot
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views import generic


class AdminHoneypot(generic.FormView):
    template_name = 'django_trap/login.html'
    form_class = HoneypotLoginForm
    store_pw = getattr(settings, 'DJANGO_TRAP_STORE_PW', False)

    def dispatch(self, request, *args, **kwargs):
        if not request.path.endswith('/'):
            return redirect(request.path + '/', permanent=True)
        # Django 1.7 redirects the user to an explicit login view with
        # a next parameter, so emulate that if needed.
        if django.VERSION >= (1, 7):
            login_url = reverse('django_trap:login')
            if request.path != login_url:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path(), login_url)
        return super(AdminHoneypot, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(AdminHoneypot, self).get_context_data(**kwargs)
        path = self.request.get_full_path()
        context.update({
            'app_path': path,
            REDIRECT_FIELD_NAME: path,
            'title': _('Log in'),
        })
        return context

    def form_valid(self, form):
        return self.form_invalid(form)

    def form_invalid(self, form):
        instance = LoginAttempt.objects.create(
            username=self.request.POST.get('username'),
            password=self.request.POST.get('password') if self.store_pw else _("<password not stored>"),
            session_key=self.request.session.session_key,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            path=self.request.get_full_path(),
        )
        honeypot.send(sender=LoginAttempt, instance=instance, request=self.request)
        return super(AdminHoneypot, self).form_invalid(form)
