from sqlalchemy.orm import Session

from app.models.db import Info






def get_info(db : Session) -> list[Info]:
    return db.query(Info).first()