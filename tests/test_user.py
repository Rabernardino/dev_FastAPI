from http import HTTPStatus

from fast_zero.schemas import UserPublic

# def test_read_root_deve_retornar_ok_e_ola_mundo(client):
#     response = client.get('/')  # Act (ação)

#     assert response.status_code == HTTPStatus.OK  # Assert (afirmação)
#     assert response.json() == {'message': 'Olar mundo!'}


def test_create_user(client):
    # Testando a criação de usuario passando o schema utilizado, neste caso
    # o UserSchema. O retorno será validado no UserPublic, como feito.

    response = client.post(
        '/users/',
        json={
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass',
        },
    )

    # Validando se o codigo retornado do created esta correto
    assert response.status_code == HTTPStatus.CREATED

    # Validando o retorno no UserPublic
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
    }


def test_create_user_username(client):
    # Testando a criação de usuario passando o schema utilizado, neste caso
    # o UserSchema. O retorno será validado no UserPublic, como feito.

    response = client.post(
        '/users/',
        json={
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass',
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    # Validando se o codigo retornado do created esta correto


def test_read_user(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_one_user(client, user):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
    }


def test_read_user_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'testpass',
            'id': 1,
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'bob',
        'email': 'bob@example.com',
    }


def test_update_user_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'testpass',
            'id': 1,
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enought permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted.'}


def test_delete_user_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enought permissions'}
