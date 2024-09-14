from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_without_sub(client):
    data_withou_sub = {}

    token_without_sub = create_access_token(data=data_withou_sub)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token_without_sub}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_current_user_wrong_user(client):
    data_withou_sub = {'sub': 'teste'}

    token_without_sub = create_access_token(data=data_withou_sub)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token_without_sub}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
