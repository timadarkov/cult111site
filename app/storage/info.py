from sqlalchemy.orm import Session

from app.models.info import Info


def get_info(db: Session) -> list[Info]:
    return db.query(Info).first()
