

def get_name_and_lot_from_url_query_dict(request):
    """Get first_name and last_name from a request object in a dict.
    """

    qs_dict = {param: request.GET[param] for param
               in ['name', 'lot_number', 'manufacturer']
               if param in request.GET}

    return qs_dict
