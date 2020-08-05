from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.utils.translation import ugettext_lazy as _
from osler.core import validators


class Language(models.Model):
    """A natural language, spoken by a provider or patient.
    """
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=30, primary_key=True)

    def __str__(self):
        return self.name

    def short_name(self):
        return self.name[0]


class User(AbstractUser):

    # more inclusive of name patterns around the world
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    phone = models.CharField(max_length=40, null=True, blank=True)

    languages = models.ManyToManyField(
        Language,
        help_text="Specify here languages that are spoken at a "
                            "level sufficient to be used for medical "
                            "communication.")
    gender = models.ForeignKey(Gender, null=True, on_delete=models.PROTECT)

    active_role = models.ForeignKey(
        Group, 
        null=True, 
        related_name="active_role", 
        on_delete=models.PROTECT
        )
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def has_active_perm(self, permission_name):
        '''Similar to django.contrib.auth.models.User.has_perm(), but permissions depend
        on only the active role.'''
        split = permission_name.index('.')
        app_label = permission_name[:split]
        codename = permission_name[split+1:]
        return self.active_role.permissions.filter(codename=codename, content_type__app_label=app_label).exists()


