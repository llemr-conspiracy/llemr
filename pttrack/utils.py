import string
from django.db.models import Q
from . import models


def all_variations(name):
    """all_variations is a function that is used to help search for all
    variations of a string that have either added, removed, or changed
    1 letter. Function returns a list of all variations of the input string.
    """
    all_vars = []
    if name is None or len(name) == 0:
        return all_vars
    if len(name) == 1:
        all_vars.append(name)
        return all_vars
    else:
        # try all variations of switching letters, other than first letter
        for i in range(1, len(name)):
            # remove letter
            all_vars.append(name[:i] + name[i+1:])
            # change letter and add letter
            for j in string.ascii_lowercase:
                all_vars.append(name[:i] + j + name[i+1:])
                all_vars.append(name[:i] + j + name[i:])

        all_vars.append(name)
        return all_vars


def return_duplicates(first_name_str, last_name_str):
    """search database for all variations of first and last name off by 1
    letter (except for first letter must be correct) and return matching
    results.  First name may also be abbreviated (to cover cases like
    ben and benjamin)
    """
    first_name_var = all_variations(first_name_str.capitalize())
    last_name_var = all_variations(last_name_str.capitalize())
    if len(first_name_var) == 0 or len(last_name_var) == 0:
        return
    return models.Patient.objects.filter(
        (Q(first_name__in=first_name_var) |
         Q(first_name__startswith=first_name_str)) &
        Q(last_name__in=last_name_var))

def get_names_from_url_query_dict(request):
    """Get first_name and last_name from a request object in a dict.
    """

    qs_dict = {param: request.GET[param] for param
               in ['first_name', 'last_name']
               if param in request.GET}

    return qs_dict
