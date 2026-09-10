from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.users import User


def add_user(db: Session, user: User) -> User:
    db.add(user)
    return user


def get_users(db: Session, username: str | None = None, email: str | None = None, nickname: str | None = None, is_active: bool | None = None, is_verified: bool | None = None,
              ) -> list[User]:
    query = db.query(User)

    if username is not None:
        query = query.filter(User.username == username)
    if email is not None:
        query = query.filter(User.email == email)
    if nickname is not None:
        query = query.filter(User.nickname == nickname)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    return query.all()


def get_user_by_username(db: Session, username: str) -> User | None:
    return (db.query(User).filter(User.username == username).first())


def get_user_by_id(db: Session, id: int) -> User | None:
    return (db.query(User).filter(User.id == id).first())
