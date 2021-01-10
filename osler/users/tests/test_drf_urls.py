import pytest
from django.urls import resolve, reverse

from osler.users.models import User

pytestmark = pytest.mark.django_db


def test_user_detail(user: User):
    assert (
        reverse("api:user-detail", kwargs={"username": user.username})
        == f"/api/user/{user.username}/"
    )
    assert resolve(f"/api/user/{user.username}/").view_name == "api:user-detail"


def test_user_list():
    assert reverse("api:user-list") == "/api/user/"
    assert resolve("/api/user/").view_name == "api:user-list"


def test_user_me():
    assert reverse("api:user-me") == "/api/user/me/"
    assert resolve("/api/user/me/").view_name == "api:user-me"
