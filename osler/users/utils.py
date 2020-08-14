from django.contrib.auth.models import Group, Permission


def get_active_role(request):
    """Given a request, process which of the user's groups is "active".

    This is used to determine which type of user to sign a note as, for
    example.
    """

    active_role_pk = request.session['active_role_pk']
    active_role = Group.objects.get(pk=active_role_pk)
    return active_role


def group_has_perm(group, perm: str):
    """Checks that a group has a certain permission.
    Name permission as '<app_label>.<codename>'"""

    split = perm.index('.')
    app_label = perm[:split]
    codename = perm[split+1:]
    return group.permissions.filter(codename=codename, content_type__app_label=app_label).exists()


def group_has_perms(group, perms):
    """Checks that a group has been granted a tuple of perms"""

    return all(group_has_perm(group, perm) for perm in perms)

