from sqlalchemy.orm import Session
from models.model import ArticleType,Category,Color,Gender,Season,SubCategory,UsageType, ImageProduct
from schemas import schema

def get_color(db: Session, name: str):
    return db.query(Color).filter(Color.name == name).first()

def get_colors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Color).offset(skip).limit(limit).all()

def get_season(db: Session, name: str):
    return db.query(Season).filter(Season.name == name).first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Season).offset(skip).limit(limit).all()

def get_gender(db: Session, name: str):
    return db.query(Gender).filter(Gender.gender == name).first()

def get_genders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Gender).offset(skip).limit(limit).all()

def get_usage_type(db: Session, name: str):
    return db.query(UsageType).filter(
            UsageType.name == name).first()

def get_usage_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UsageType).offset(skip).limit(limit).all()

def get_category(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()

def get_category_by_id(db: Session, id: int):
    return db.query(Category).filter(Category.id == id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Category).offset(skip).limit(limit).all()

def get_subcategory(db: Session, name: str):
    return db.query(SubCategory).filter(
            SubCategory.name == name).first()

def get_subcategory_by_id(db: Session, id: int):
    return db.query(SubCategory).filter(
            SubCategory.id == id).first()

def get_subcategories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SubCategory).offset(skip).limit(limit).all()

def get_article_type(db: Session, name: str):
    return db.query(ArticleType).filter(
            ArticleType.name == name).first()

def get_article_types(db: Session, skip: int = 0, limit: int = 200):
    return db.query(ArticleType).offset(skip).limit(limit).all()

def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ImageProduct).offset(skip).limit(limit).all()

def get_images_and_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(
                    ImageProduct.id,
                    ImageProduct.path,
                    Gender.gender,
                    Color.name.label('color'),
                    Season.name.label('season'),
                    ArticleType.name.label('article'),
                    Category.name.label('category'),
                    SubCategory.name.label('sub_category'),
                    UsageType.name.label('usage_type')
                    ).join(Gender, Gender.id == ImageProduct.id_gender
                    ).join(Color, Color.id == ImageProduct.id_color
                    ).join(Season, Season.id == ImageProduct.id_season
                    ).join(ArticleType, ArticleType.id == ImageProduct.id_articletype
                    ).join(SubCategory, SubCategory.id == ArticleType.id_subcategory
                    ).join(Category, Category.id == SubCategory.id_category
                    ).join(UsageType, UsageType.id == ImageProduct.id_usagetype
                    ).offset(skip).limit(limit).all()

def create_color(db: Session, color: schema.Color):
    db_color = Color(name=color.name)
    db.add(db_color)
    db.commit()
    db.refresh(db_color)
    return db_color

def create_image_product(db: Session, image: schema.ImageProduct):
    db_image = ImageProduct(
                                path=image.path,
                                id_usagetype=image.id_usagetype,
                                id_gender=image.id_gender,
                                id_season=image.id_season,
                                id_color=image.id_color,
                                id_articletype=image.id_articletype)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image