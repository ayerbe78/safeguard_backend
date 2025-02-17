import re

SENSITIVE_KEYS = ["password", "token", "access", "refresh", "AUTHORIZATION"]


def get_headers(request=None):
    """
    Function:       get_headers(self, request)
    Description:    To get all the headers from request
    """
    regex = re.compile("^HTTP_")
    return dict(
        (regex.sub("", header), value)
        for (header, value) in request.META.items()
        if header.startswith("HTTP_")
    )


def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
    except:
        return ""


def mask_sensitive_data(data, mask_api_parameters=False):
    """
    Hides sensitive keys specified in sensitive_keys settings.
    Loops recursively over nested dictionaries.
    When the mask_api_parameters parameter is set, the function will
    instead iterate over sensitive_keys and remove them from an api
    URL string.
    """

    if type(data) != dict:
        if mask_api_parameters and type(data) == str:
            for sensitive_key in SENSITIVE_KEYS:
                data = re.sub(
                    "({}=)(.*?)($|&)".format(sensitive_key),
                    "\g<1>***FILTERED***\g<3>".format(sensitive_key.upper()),
                    data,
                )
        return data

    for key, value in data.items():
        if key in SENSITIVE_KEYS:
            data[key] = "***FILTERED***"

        if type(value) == dict:
            data[key] = mask_sensitive_data(data[key])

        if type(value) == list:
            data[key] = [mask_sensitive_data(item) for item in data[key]]

    return data


def get_current_user(request=None):
    """
    Function:       get_current_user(self, request)
    Description:    To get the current user of the request
    """
    user = request.user if request.user else None

    return user
