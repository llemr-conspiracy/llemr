# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class DrugCategory(models.Model):

    name = models.CharField(max_length=100, blank=False, primary_key=True)

    def __str__(self):
        return '{}'.format(self.name)


class Formulation(models.Model):

    dose_mg = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.dose_mg)


class Drugs(models.Model):

    name = models.CharField(max_length=100, blank=False)

    total_inventory = models.IntegerField(default=0, null=True, blank=True)

    category = models.ForeignKey(DrugCategory)

    dose = models.ForeignKey(Formulation)

    def __str__(self):
        return 'Category: {0} Name: {1} Dose: {2}'.format(self.category, self.name, self.dose)
