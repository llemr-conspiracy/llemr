from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    active_role = models.ForeignKey(Group, null=True, related_name="active_role", on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def has_permission(self, permission_name):
        '''Similar to django.contrib.auth.models.User.has_perm(), but permissions depend
        on only the active role.'''
        split = permission_name.index('.')
        app_label = permission_name[:split]
        codename = permission_name[(split+1):]
        return self.active_role.permissions.filter(codename=codename, content_type__app_label=app_label).exists()
