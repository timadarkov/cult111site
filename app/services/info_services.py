from sqlalchemy.orm import Session
from app.storage import info as info_storage
from app.schemas import info


def get_info(db: Session):
    return info_storage.get_info(db)


def add_info(data: info.InfoAdd, db: Session):
    return info_storage.add_info(db, data)


def update_info(slug: str, data: info.InfoUpdate, db: Session):
    return info_storage.update_info(db=db, slug=slug, data=data)
