from sqlalchemy.orm import Session
from app.schemas.info import InfoUpdate
from app.models.info import Info


def get_info(db: Session) -> list[Info]:
    return db.query(Info).filter(Info.is_visible == True).all()


def update_info(db: Session, info: InfoUpdate):
    record = db.query(Info).first()

    if record is None:
        return None

    changes = info.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record
