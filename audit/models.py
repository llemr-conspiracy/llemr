from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from pttrack import models as core_models


class PageviewRecord(models.Model):

    HTTP_METHODS = ['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'DELETE',
                    'CONNECT', 'OPTIONS', 'TRACE']

    user = models.ForeignKey(
        User,
        blank=True, null=True,
        on_delete=models.DO_NOTHING
    )
    user_ip = models.GenericIPAddressField()
    role = models.ForeignKey(
        core_models.ProviderType,
        on_delete=models.DO_NOTHING,
        blank=True, null=True)

    method = models.CharField(
        max_length=max(len(v) for v in HTTP_METHODS),
        choices=[(v, v) for v in HTTP_METHODS])

    url = models.URLField(max_length=256)
    referrer = models.URLField(max_length=256, blank=True, null=True)

    status_code = models.PositiveSmallIntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s by %s to %s at %s' % (self.method, self.user, self.url,
                                         self.timestamp)
