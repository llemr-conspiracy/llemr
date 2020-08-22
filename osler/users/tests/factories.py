import factory

from typing import Any, Sequence

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q


class GroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Group

    name = factory.Sequence(lambda n: "Generic Group #%s" % n)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        self.permissions.add(
            *Permission.objects.all()
        )


class VolunteerGroupFactory(GroupFactory):

    name = factory.Sequence(lambda n: "Volunteer Group #%s" % n)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        self.permissions.add(
            *Permission.objects.exclude(
                Q(codename__startswith='sign_') | Q(codename='case_manage_Patient') | 
                Q(codename='activate_Patient')
            )
        )


class CaseManagerGroupFactory(GroupFactory):

    name = factory.Sequence(lambda n: "Case Manager Group #%s" % n)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        self.permissions.add(
            *Permission.objects.exclude(codename__startswith='sign_')
        )


class AttendingGroupFactory(GroupFactory):

    name = factory.Sequence(lambda n: "Attending Group #%s" % n)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        self.permissions.add(
            *Permission.objects.exclude(
                Q(codename='case_manage_Patient') | Q(codename='activate_Patient')
            )
        )


class NoPermGroupFactory(GroupFactory):

    name = factory.Sequence(lambda n: "No Permission Group #%s" % n)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        pass


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    email = factory.Faker("email")
    name = factory.Faker("name")

    @factory.post_generation
    def username(self, create: bool, extracted: Sequence[Any], **kwargs):
        self.username = (
            extracted
            if extracted
            else factory.Faker("user_name").generate(extra_kwargs={})
        )

    @factory.post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else factory.Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).generate(extra_kwargs={})
        )
        self.set_password(password)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # triggered with: UserFactory.create(groups=(group1, group2, group3))
        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)


# constants to be used across tests
attesting_roles = set([AttendingGroupFactory])
nonattesting_roles = set([CaseManagerGroupFactory, VolunteerGroupFactory])
all_roles = attesting_roles | nonattesting_roles
