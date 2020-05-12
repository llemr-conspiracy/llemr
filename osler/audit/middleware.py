from __future__ import unicode_literals
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.apps import apps

from osler.core.models import ProviderType


class AuditMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

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

        if user_ip not in settings.OSLER_AUDIT_BLACK_LIST:
            PageviewRecord = apps.get_app_config('audit').get_model(
                model_name='PageviewRecord')

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
