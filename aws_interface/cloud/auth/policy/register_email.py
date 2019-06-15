def can_register(extra, password_meta):
    """
    :param extra: {str: any?}, additional fields that the user will fill out when registering such as gender and birth.
    :param password_meta: {'count': int, 'count_number': int, 'count_uppercase': int, 'count_lowercase': int,
                           'count_special': int}, Meta information for passwords
    :return: bool, Determines if user can register.
    """
    if password_meta['count'] > 6:
        return True
    return False
