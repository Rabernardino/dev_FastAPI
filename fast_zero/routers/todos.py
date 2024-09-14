from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[Session, Depends(get_session)]
T_Current_User = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
def create_todo(session: T_Session, user: T_Current_User, todo: TodoSchema):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(
    session: T_Session,
    current_user: T_Current_User,
    title: str | None = None,
    description: str | None = None,
    state: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    db_todo = select(Todo).where(Todo.user_id == current_user.id)

    if title:
        db_todo = db_todo.filter(Todo.title.contains(title))

    if description:
        db_todo = db_todo.filter(Todo.description.contains(description))

    if state:
        db_todo = db_todo.filter(Todo.state == state)

    db_todos = session.scalars(db_todo.offset(offset).limit(limit)).all()

    return {'todos': db_todos}


@router.delete('/', response_model=Message)
def delete_todo(
    session: T_Session, current_user: T_Current_User, todo_id: int
):
    db_todo = session.scalar(
        select(Todo).where(
            (Todo.user_id == current_user.id) & (todo_id == Todo.id)
        )
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    session.delete(db_todo)
    session.commit()

    return {'message': 'Task has been deleted'}


@router.patch('/', response_model=TodoPublic)
def update_todo(
    session: T_Session,
    current_user: T_Current_User,
    todo_id: int,
    todo: TodoUpdate,
):
    db_todo = session.scalar(
        select(Todo).where(
            (Todo.user_id == current_user.id) & (todo_id == Todo.id)
        )
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
