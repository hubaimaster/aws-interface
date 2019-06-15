def can_register(extra, password_meta):
    """
    :param extra: {str: any?}, additional fields that the user will fill out when registering such as ip and region.
    :param password_meta: None, Not available on guest register.
    :return: bool, Determines if user can register.
    """
    return True
