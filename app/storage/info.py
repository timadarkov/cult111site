from sqlalchemy.orm import Session
from app.schemas.info import InfoUpdate, InfoAdd
from app.models.info import Info


def get_info(db: Session) -> list[Info]:
    return db.query(Info).filter(Info.is_visible == True).all()


def add_info(db: Session, data: InfoAdd):
    info = Info(
        slug=data.slug,
        info=data.info,
        owners=data.owners,
        contacts=data.contacts,
    )

    db.add(info)
    db.commit()
    db.refresh(info)
    return info


def update_info(db: Session, slug: str, data: InfoUpdate):
    record = db.query(Info).filter(Info.slug == slug).first()

    if record is None:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record
