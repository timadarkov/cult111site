from database import SessionLocal

from app.storage import info as info_storage






def get_info():
    db = SessionLocal()
    try:
        company = info_storage.get_info(db)   
        return {"info": company.info, "owners": company.owners, "contacts": company.contacts}
    finally:
        db.close()
