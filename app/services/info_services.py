from sqlalchemy.orm import Session
from app.storage import info as info_storage


def get_info(db: Session):
    return info_storage.get_info(db)


def update_info(info, current_admin, db):
    return info_storage.update_info(db, info)
