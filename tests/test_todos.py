from http import HTTPStatus

from fast_zero.models import TodoState
from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test',
            'description': 'test_description',
            'state': 'draft',
        },
    )

    assert response.json()['id'] == 1
    assert response.json()['title'] == 'test'
    assert response.json()['description'] == 'test_description'
    assert response.json()['state'] == 'draft'


def test_list_todos_should_return_5_todos(session, client, user, token):
    excepted_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == excepted_todos


def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    excepted_todos = 2
    session.bulk_save_objects(
        TodoFactory.create_batch(5, title='a', user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == excepted_todos


def test_list_todos_filter_title_should_return_5_todos(
    session, client, user, token
):
    excepted_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, title='test title', user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todos/?title=test title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == excepted_todos


def test_list_todos_filter_description_should_return_5_todos(
    session, client, user, token
):
    excepted_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5, description='test description', user_id=user.id
        )
    )
    session.commit()

    response = client.get(
        '/todos/?description=test description',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == excepted_todos


def test_list_todos_filter_state_should_return_5_todos(
    session, client, user, token
):
    excepted_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, state=TodoState.done, user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todos/?state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == excepted_todos


def test_list_todos_filter_combined_should_return_5_todos(
    session, client, user, token
):
    excepted_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            title='test_combined',
            description='desc_combined',
            state=TodoState.draft,
            user_id=user.id,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            2,
            title='combined',
            description='combined',
            state=TodoState.done,
            user_id=user.id,
        )
    )

    session.commit()

    response = client.get(
        '/todos/?title=test&description=desc&state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == excepted_todos


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.delete(
        f'/todos/?todo_id={todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'message': 'Task has been deleted'}


def test_delete_todo_wrong_todo_id(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.delete(
        '/todos/?todo_id=10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Task not found'


def test_update_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f'/todos/?todo_id={todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Teste'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'Teste'


def test_update_todo_wrong(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        '/todos/?todo_id=10',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Teste'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Task not found'
