from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords

from osler.core import validators


class User(AbstractUser):

    class Meta:
        ordering = ["last_name",]
        permissions = [
            ('view_clinic_datadashboard', _("Can view clinic data dashboard"))
        ]

    # more inclusive of name patterns around the world
    name = models.CharField("Preferred name", blank=True, max_length=255)

    phone = models.CharField(max_length=40, null=True, blank=True)

    languages = models.ManyToManyField(
        "core.Language",
        help_text="Specify here languages that are spoken at a "
                            "level sufficient to be used for medical "
                            "communication.")
    gender = models.ForeignKey("core.Gender", null=True, on_delete=models.PROTECT)

    history = HistoricalRecords()

    needs_updating = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self):
        if self.first_name and self.last_name:
            first = self.name if self.name else self.first_name
            return '%s, %s' % (self.last_name, first)
        else:
            return self.username

    def get_full_name(self):
        first = self.name if self.name else self.first_name
        full_name = '%s %s' % (first, self.last_name)
        return full_name.strip()
