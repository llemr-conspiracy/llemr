from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from simple_history.models import HistoricalRecords

from osler.core import validators


class User(AbstractUser):

    # more inclusive of name patterns around the world
    name = models.CharField(_("Preferred name"), blank=True, max_length=255)

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
