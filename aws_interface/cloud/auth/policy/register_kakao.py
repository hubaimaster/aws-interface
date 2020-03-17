def can_register(extra, password_meta):
    """
    :param extra: {str: any?}, additional fields that the user will fill out when registering such as gender and birth.
    :param password_meta: None, Not available on Kakao register.
    :return: bool, Determines if user can register.
    """
    return True
