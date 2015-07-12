from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse_lazy


def provider_exists(user):
    return hasattr(user, 'provider')


def provider_required(func):
    '''Provides composite multi-decorator support for the standard login
    procedure wrapping most views.'''

    func = login_required(func)

    func = user_passes_test(provider_exists,
                            login_url=reverse_lazy('new-provider'))(func)

    return func
