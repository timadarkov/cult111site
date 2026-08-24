
from sqlalchemy.orm import Session

from app.models.db import Brands, Info, Category, Products


def get_info(db : Session) -> list[Info]:
    return db.query(Info).first()

def get_categories(db : Session) -> list[Category]:
    return db.query(Category).all()


def get_brands(db : Session) -> list[Brands]:
    return db.query(Brands).all()

def get_products(db : Session) -> list[Products]:
    return db.query(Products).all()


