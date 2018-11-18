from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from pttrack import models as core_models


class PageviewRecord(models.Model):

    HTTP_VERBS = ['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'DELETE']

    user = models.ForeignKey(User)
    user_ip = models.GenericIPAddressField()
    user_role = models.ForeignKey(core_models.ProviderType,
                                  blank=True, null=True)

    verb = models.CharField(
        max_length=max(len(v) for v in HTTP_VERBS),
        choices=zip(*(HTTP_VERBS, HTTP_VERBS)))
    url = models.URLField(max_length=256)
    referrer = models.URLField(max_length=256)

    status_code = models.PositiveSmallIntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)
