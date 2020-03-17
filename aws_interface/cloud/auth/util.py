

def already_has_account_email(email, resource):
    items, _ = resource.db_query('user', [
        (None, ('email', 'eq', email)),
    ])
    if items:
        return True
    else:
        return False
