from getpass import getpass

from sqlalchemy import select

from database import SessionLocal
from app.models.users import User
from app.auth.utils import hash_password


def create_first_admin() -> None:
    with SessionLocal() as session:
        existing_admin = session.scalar(
            select(User).where(User.is_admin.is_(True))
        )

        if existing_admin:
            print("Admin already exists. Bootstrap is disabled.")
            return

        username = input("Username: ").strip()
        nickname = input("Nickname: ").strip()
        email = input("Email: ").strip() or None

        password = getpass("Password: ")
        password_repeat = getpass("Repeat password: ")

        if not username:
            print("Username cannot be empty")
            return

        if not nickname:
            print("Nickname cannot be empty")
            return

        if not password:
            print("Password cannot be empty")
            return

        if password != password_repeat:
            print("Passwords do not match")
            return

        admin = User(
            username=username,
            nickname=nickname,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            is_verified=True,
            is_admin=True,
        )

        session.add(admin)
        session.commit()

        print(f"First admin '{username}' created successfully.")


if __name__ == "__main__":
    create_first_admin()
