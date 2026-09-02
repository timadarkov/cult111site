from sqlalchemy.orm import Session

from app.models.users import User


def add_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
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
