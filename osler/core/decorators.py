from __future__ import unicode_literals
from functools import wraps
from urllib.parse import urlparse

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse_lazy
from django.shortcuts import resolve_url


def user_is_init(user):
    return user.groups.exists()


def active_role_set(session):
    return 'active_role_set' in session and session['active_role_set']


def session_passes_test(test_func, fail_url,
                        redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the session passes the given test,
    redirecting to the choice page if necessary. The test should be a callable
    that takes the session object and returns True if the session passes. It's
    nearly a carbon copy of django.contrib.auth.decorators.user_passes_test.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.session):
                return view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()
            resolved_url = resolve_url(fail_url)

            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.

            scheme, netloc = urlparse(resolved_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not scheme or scheme == current_scheme) and
                    (not netloc or netloc == current_netloc)):
                path = request.get_full_path()

            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_url, redirect_field_name)

        return _wrapped_view
    return decorator


def active_role_required(func):
    return session_passes_test(
        active_role_set,
        fail_url=reverse_lazy('core:choose-role'))(func)


def user_init_required(func):
    return user_passes_test(
        user_is_init,
        login_url=reverse_lazy('core:user-init'))(func)
