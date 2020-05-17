import datetime
import os

from django.conf import settings
from django.db.models.signals import post_save

import factory
from factory import Faker
from factory.django import DjangoModelFactory, mute_signals

from osler.core import models


class ActionInstructionFactory(DjangoModelFactory):

    class Meta:
        model = models.ActionInstruction

    instruction = factory.Sequence(lambda n: 'Action instruction #%s' % n)

class ActionItemFactory(DjangoModelFactory):

    class Meta:
        model = models.ActionItem

    instruction = factory.SubFactory(ActionInstructionFactory)
    author_type = factory.LazyAttribute(lambda ai: ai.author.groups.first())


class GenderFactory(DjangoModelFactory):

    class Meta:
        model = models.Gender

    # Genders flip flop between "Male" and "Female" with each one generated
    name = factory.Sequence(lambda n: "Gender %03d" % n)


@mute_signals(post_save)
class ProviderFactory(DjangoModelFactory):
    class Meta:
        model = models.Provider

    # We pass in provider=None to prevent UserFactory from creating another
    # provider (this disables the RelatedFactory)
    user = factory.SubFactory('osler.users.tests.factories.UserFactory',
                              provider=None)
    gender = factory.SubFactory(GenderFactory)


class LanguageFactory(DjangoModelFactory):

    class Meta:
        model = models.Language

    name = factory.Iterator(["English", "German", "Spanish", "Klingon"])


class ContactMethodFactory(DjangoModelFactory):

    class Meta:
        model = models.ContactMethod

    name = factory.Iterator(["Telephone", "Banana Phone",
                             "Telekinesis", "Carrier Pidgeon",
                             "Tin Cans + String", "Female", "Other"])


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

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of languages were passed in, use them
            for language in extracted:
                self.languages.add(language)

    @factory.post_generation
    def ethnicities(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of ethnicities were passed in, use them
            for ethnicity in extracted:
                self.ethnicities.add(ethnicity)

    @factory.post_generation
    def case_managers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of case_managers were passed in, use them
            for manager in extracted:
                self.case_managers.add(manager)


class DocumentTypeFactory(DjangoModelFactory):

    class Meta:
        model = models.DocumentType

    name = factory.Sequence(lambda n: "Silly Picture Type #%s?" % n)


class DocumentFactory(DjangoModelFactory):

    class Meta:
        model = models.Document

    title = factory.Sequence(lambda n: "who done it #%s?" % n)
    comments = Faker('paragraph')

    document_type = factory.SubFactory(DocumentTypeFactory)
    image = factory.django.FileField(
        from_path=os.path.join(settings.FIXTURE_DIRS[0], 'media', 'test.jpg'))
    patient = factory.SubFactory(PatientFactory)
    # author = factory.Iterator(get_user_model().objects.all())
    # author_type = factory.SubFactory(user_factories.GroupFactory)
