from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpRequest

from .models import PageviewRecord

from pttrack.models import ProviderType

class ErrorEmailMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #it said I needed a call function
        return self.get_response(request)

    def process_exception(self, request, exception):
        try:
           logged_in_info = ''
           if request.user and request.user.is_authenticated():
               logged_in_info = "%s" % request.user
               if request.user.email:
                   logged_in_info += ' %s' % request.user.email
               if request.user.first_name or request.user.last_name:
                   logged_in_info += ' (%s %s)' % \
                     (request.user.first_name, request.user.last_name)
           if logged_in_info:
               request.META['LOGGED-IN-USER'] = logged_in_info
        except:
           logging.debug("Unable to debug who was logged in", exc_info=True)


class AuditMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        response = self.get_response(request)

        # this header is used by nginx, etc to indicate which IP address
        # the original request was from
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            user_ip = x_forwarded_for.split(',')[0]
        else:
            user_ip = request.META.get('REMOTE_ADDR')

        role = request.session.get('clintype_pk', None)

        if role is not None:
            role = ProviderType.objects.get(pk=role)

        PageviewRecord.objects.create(
            user=(None if isinstance(request.user, AnonymousUser)
                  else request.user),
            role=role,
            user_ip=user_ip,
            method=request.method,
            url=request.get_full_path(),
            referrer=request.META.get('HTTP_REFERER', None),
            status_code=response.status_code
        )

        return response
