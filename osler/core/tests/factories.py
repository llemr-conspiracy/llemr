import datetime

from django.db.models.signals import post_save

import factory
from factory.django import DjangoModelFactory, mute_signals

from osler.core import models


class ActionItemFactory(DjangoModelFactory):

    class Meta:
        model = models.ActionItem


@mute_signals(post_save)
class ProviderFactory(DjangoModelFactory):
    class Meta:
        model = models.Provider

    # We pass in profile=None to prevent UserFactory from creating another
    # profile (this disables the RelatedFactory)
    user = factory.SubFactory('osler.users.tests.factories.UserFactory',
                              profile=None)


class GenderFactory(DjangoModelFactory):

    class Meta:
        model = models.Gender

    # Genders flip flop between "Male" and "Female" with each one generated
    name = factory.Sequence(lambda n: "Male" if n % 2 == 0 else "Female")


class LanguageFactory(DjangoModelFactory):

    class Meta:
        model = models.Language

    name = "Klingon"


class ContactMethodFactory(DjangoModelFactory):

    class Meta:
        model = models.ContactMethod

    name = "Tin Cans + String"


class PatientFactory(DjangoModelFactory):

    class Meta:
        model = models.Patient

    first_name = "Juggie"
    last_name = "Brodeltein"
    middle_name = "Bayer"
    phone = '+49 178 236 5288',
    languages = factory.SubFactory(LanguageFactory),
    gender = factory.SubFactory(GenderFactory)
    address = 'Schulstrasse 9'
    city = 'Munich'
    state = 'BA'
    country = 'Germany'
    zip_code = '63108'
    pcp_preferred_zip = '63018'
    date_of_birth = datetime.date(1990, 1, 1)
    patient_comfortable_with_english = False
    ethnicities = "Klingon",
    preferred_contact_method = factory.SubFactory(ContactMethodFactory)
