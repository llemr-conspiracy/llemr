import factory

from typing import Any, Sequence

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    name = factory.Faker("name")

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
