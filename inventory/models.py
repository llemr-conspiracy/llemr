# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class drugs(models.Model):

    name = models.CharField(max_length=100, blank=False)        # name of drug

    dose = models.IntegerField()

    total_inventory = models.IntegerField()

    choices = (
        ('Available', 'Item ready to be dispensed'),
        ('Out of stock', 'Item currently depleted'),
        ('Restocking', 'Item being restocked')
    )
    # Available, Out of Stock, Restocking
    status = models.CharField(max_length=20, default="Out of Stock")

    class Meta:
        abstract = True

    def __str__(self):
        return 'Name: {0} Dose: {1}'.format(self.name, self.dose)


class Supplements(drugs):
    pass


class Allergy(drugs):
    pass


class Cardiovascular(drugs):
    pass


class Pain_Relief(drugs):
    pass


class Antibiotics(drugs):
    pass


class Endocrine_and_GI(drugs):
    pass


class Respiratory(drugs):
    pass


class Other(drugs):
    pass
