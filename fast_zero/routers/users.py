from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])


T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_users(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exist',
            )

        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exist',
            )

    db_user = User(user.username, get_password_hash(user.password), user.email)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(session: T_Session, limit: int = 10, skip: int = 0):
    users = session.scalars(select(User).limit(limit).offset(skip))

    return {'users': users}


@router.get('/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_one_user(id: int, session: T_Session):
    user = session.scalar(select(User).where(User.id == id))

    return user


@router.put('/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_users(
    id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enought permissions',
        )

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email

    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enought permissions',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted.'}
