from sqlalchemy.orm import Session
from models import model
from schemas import schema

def get_color(db: Session, name: str):
    return db.query(model.Color).filter(model.Color.name == name).first()

def get_colors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Color).offset(skip).limit(limit).all()

def get_season(db: Session, name: str):
    return db.query(model.Season).filter(model.Season.name == name).first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Season).offset(skip).limit(limit).all()

def get_gender(db: Session, name: str):
    return db.query(model.Gender).filter(model.Gender.gender == name).first()

def get_genders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Gender).offset(skip).limit(limit).all()

def get_usage_type(db: Session, name: str):
    return db.query(model.UsageType).filter(
            model.UsageType.name == name).first()

def get_usage_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.UsageType).offset(skip).limit(limit).all()

def get_category(db: Session, name: str):
    return db.query(model.Category).filter(model.Category.name == name).first()

def get_category_by_id(db: Session, id: int):
    return db.query(model.Category).filter(model.Category.id == id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Category).offset(skip).limit(limit).all()

def get_subcategory(db: Session, name: str):
    return db.query(model.SubCategory).filter(
            model.SubCategory.name == name).first()

def get_subcategory_by_id(db: Session, id: int):
    return db.query(model.SubCategory).filter(
            model.SubCategory.id == id).first()

def get_subcategories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.SubCategory).offset(skip).limit(limit).all()

def get_article_type(db: Session, name: str):
    return db.query(model.ArticleType).filter(
            model.ArticleType.name == name).first()

def get_article_types(db: Session, skip: int = 0, limit: int = 200):
    return db.query(model.ArticleType).offset(skip).limit(limit).all()

def create_color(db: Session, color: schema.Color):
    db_color = model.Color(name=color.name)
    db.add(db_color)
    db.commit()
    db.refresh(db_color)
    return db_color