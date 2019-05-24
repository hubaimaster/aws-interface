import aws_interface

EMAIL = 'email@example.com'
PASSWORD = 'password_for_test'
DB_PARTITION = 'test'
client = aws_interface.Client()


def test_auth():
    response = client.auth_register(EMAIL, PASSWORD, {'age': 24, 'nation': 'korea'})
    print(response)
    response = client.auth_login(EMAIL, PASSWORD)
    print(response)
    response = client.auth_get_user(None)
    print(response)
    response = client.auth_logout()
    print(response)
    response = client.auth_guest()
    print(response)


def test_database():
    response = client.database_create_item(DB_PARTITION, {
        'nation': 'korea',
        'populations': 50000000
    }, ['owner'], ['owner'])
    print(response)
    response = client.database_get_item(response['item']['id'])
    print(response)
    response['item']['nation'] = 'france'
    response = client.database_update_item(response['item']['id'], response['item'])
    print(response)


def test_logic():
    response = client.logic_run_function('test2', {
        'nation': 'japan',
        'populations': 120000000
    })
    print(response)
