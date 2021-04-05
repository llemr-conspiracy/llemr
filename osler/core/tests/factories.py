import datetime
import os



#from django.contrib.auth.models import Group as group_model

#from osler.core.tests.test_views import build_user

from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.timezone import now


import factory
from factory.django import DjangoModelFactory, mute_signals

from osler.core import models
from osler.users.tests import factories as user_factories

#fixtures = ['groups']

class ActionInstructionFactory(DjangoModelFactory):

    class Meta:
        model = models.ActionInstruction

    instruction = factory.Sequence(lambda n: 'Action instruction #%s' % n)


class GenderFactory(DjangoModelFactory):

    class Meta:
        model = models.Gender

    # Genders flip flop between "Male" and "Female" with each one generated
    name = factory.Sequence(lambda n: "Gender %03d" % n)


#@mute_signals(post_save)
class ProviderFactory(DjangoModelFactory):
    class Meta:
        model = models.Provider

    user = factory.SubFactory('osler.users.tests.factories.UserFactory')
    gender = factory.SubFactory(GenderFactory)


class LanguageFactory(DjangoModelFactory):

    class Meta:
        model = models.Language

    name = factory.Iterator(["English", "German", "Spanish", "Klingon"])


class ContactMethodFactory(DjangoModelFactory):

    class Meta:
        model = models.ContactMethod
        django_get_or_create = ('name',)

    name = factory.Iterator(["Telephone", "Banana Phone",
                             "Telekinesis", "Carrier Pidgeon",
                             "Tin Cans + String", "Female", "Other"])


class EthnicityFactory(DjangoModelFactory):

    class Meta:
        model = models.Ethnicity

    name = factory.Sequence(lambda n: "Ethnicity %03d" % n)


class EncounterStatusFactory(DjangoModelFactory):

    class Meta:
        model = models.EncounterStatus
        django_get_or_create = ('name',)

    name = factory.Iterator(["Arrived", "Team in Room",
                             "Awaiting Attending", "Checkout",
                             "Awaiting Labs", "Other teams"])
    is_active = True


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
    comments = factory.Faker('paragraph')

    document_type = factory.SubFactory(DocumentTypeFactory)
    image = factory.django.FileField(
        from_path=os.path.join(settings.FIXTURE_DIRS[0], 'media', 'test.jpg'))
    patient = factory.SubFactory(PatientFactory)


class ActionItemFactory(DjangoModelFactory):

    class Meta:
        model = models.ActionItem

    patient = factory.SubFactory(PatientFactory)
    instruction = factory.SubFactory(ActionInstructionFactory)

    # really, this should automatically create a user and an author_type
    # if those things aren't specified (maybe with a post_generation hook)
    # but I can't figure out how to make that work. -JRP

class EncounterFactory(DjangoModelFactory):

    class Meta:
        model = models.Encounter

    patient = factory.SubFactory(PatientFactory)
    status = factory.SubFactory(EncounterStatusFactory)
    clinic_day = now().date()



class NoteFactory(DjangoModelFactory):
    class Meta:
        model = models.Note

    #old:
    #author = factory.SubFactory(user_factories.UserFactory)

    #author = factory.SubFactory(user_factories.UserFactory.create(groups = (factory.SubFactory(user_factories.NoPermGroupFactory))))

    #import pdb
    #pdb.set_trace()

    #fixtures = ['groups']

    #groups_to_add = Group.objects.all()
   

    #author = factory.SubFactory(user_factories.UserFactory(groups = [f() for f in groups_to_add], username = "ahkhe", password = "aoiwhe"))
    
    #what is working!

    
    
    author_type = factory.SubFactory(user_factories.NoPermGroupFactory)
    author = factory.SubFactory(user_factories.UserFactory)
    author.groups = author_type
    

    #dtype_list = models.DiagnosisType.objects.all()
    #group_list = Group.objects.all()

    #import pdb
    #pdb.set_trace()
    #author = factory.SubFactory(user_factories.UserFactory.create(groups = (group_list)))
    #author_type= author.groups.first()
   
    #author = factory.SubFactory(user_factories.UserFactory(groups = group_model.Group.objects.all()))
    #patient = factory.SubFactory(core_factories.PatientFactory)
    
    #group1 = factory.SubFactory(user_factories.VolunteerGroupFactory())
    #author = factory.SubFactory(user_factories.UserFactory.create(groups = (factory.SubFactory(user_factories.VolunteerGroupFactory))))
    #UserFactory.create(groups=(group1, group2, group3))
    #author = factory.SubFactory(user_factories.UserFactory.create(groups=group_model.objects.all()))
    #to-do: make the author_type one of the author's groups (specifically tied to each other!!)
    #author_type = factory.SubFactory(user_factories.GroupFactory)
    #my thinking with taking this out is I was looking at the user factory and there is a post_generation hook
    #in the user factory meaning that 

    #group1 = factory.SubFactory(user_factories.GroupFactory())
    #author = factory.SubFactory(user_factories.UserFactory.create(groups = (group1)))
    
    patient = factory.SubFactory(PatientFactory)

    written_datetime = datetime.date(1990, 1, 1)
    last_modified = datetime.date(1990,1,2)

