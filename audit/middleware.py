from django.contrib.auth.models import AnonymousUser

from .models import PageviewRecord

from pttrack.models import ProviderType


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
