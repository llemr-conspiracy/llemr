import factory
import datetime
from factory.django import DjangoModelFactory
from osler.inventory import models
from osler.core.tests import factories as core_factories


class DrugCategoryFactory(DjangoModelFactory):

    class Meta:
        model = models.DrugCategory

    name = factory.Iterator(["Antibiotics", "Endocrine/GI", "Supplements", "Cardiovascular"])

class MeasuringUnitFactory(DjangoModelFactory):

    class Meta:
        model = models.MeasuringUnit

    name = factory.Iterator(["mg", "ml", "IU", "%"])

class ManufacturerFactory(DjangoModelFactory):

    class Meta:
        model = models.Manufacturer

    name = factory.Iterator(["Pfizer", "Amgen", "Regeneron", "Oxford BioMedica"])

class DrugFactory(DjangoModelFactory):

    class Meta:
        model = models.Drug

    name = 'Clindamycin'
    unit = factory.SubFactory(MeasuringUnitFactory)
    dose = 100.0
    stock = 10
    expiration_date = datetime.date(2020, 1, 1)
    lot_number = 'ABCDEFGH'
    category = factory.SubFactory(DrugCategoryFactory)
    manufacturer = factory.SubFactory(ManufacturerFactory)

class DispenseHistoryFactory(DjangoModelFactory):

    class Meta:
        model = models.DispenseHistory

    dispense = 5
    drug = factory.SubFactory(DrugFactory)
    patient = factory.SubFactory(core_factories.PatientFactory)
