from sqlalchemy.orm import Session
# from database.model import ArticleType,Category,Color,Gender,Season,SubCategory,UsageType,ImageProduct,Client
from database import model
from schemas import schema
import bcrypt


def hash_password(password):
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def get_color(db: Session, name: str):
    """
    Retrieves a color from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the color to retrieve.

    Returns:
        Color: The Color object if found, otherwise None.
    """
    return db.query(model.Color).filter(model.Color.name == name).first()


def get_colors(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of colors from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[Color]: A list of Color objects.
    """
    return db.query(model.Color).offset(skip).limit(limit).all()


def get_season(db: Session, name: str):
    """
    Retrieves a season from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the season to retrieve.

    Returns:
        Season: The Season object if found, otherwise None.
    """
    return db.query(model.Season).filter(model.Season.name == name).first()


def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of seasons from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[Season]: A list of Season objects.
    """
    return db.query(model.Season).offset(skip).limit(limit).all()


def get_gender(db: Session, name: str):
    """
    Retrieves a gender from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the gender to retrieve.

    Returns:
        Gender: The Gender object if found, otherwise None.
    """
    return db.query(model.Gender).filter(model.Gender.gender == name).first()


def get_genders(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of genders from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[Gender]: A list of Gender objects.
    """
    return db.query(model.Gender).offset(skip).limit(limit).all()


def get_usage_type(db: Session, name: str):
    """
    Retrieves a usage type from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the usage type to retrieve.

    Returns:
        UsageType: The UsageType object if found, otherwise None.
    """
    return db.query(model.UsageType).filter(
        model.UsageType.name == name).first()


def get_usage_types(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of usage types from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[UsageType]: A list of UsageType objects.
    """
    return db.query(model.UsageType).offset(skip).limit(limit).all()


def get_category(db: Session, name: str):
    """
    Retrieves a category from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the category to retrieve.

    Returns:
        Category: The Category object if found, otherwise None.
    """
    return db.query(model.Category).filter(model.Category.name == name).first()


def get_category_by_id(db: Session, id: int):
    """
    Retrieves a category from the database by its ID.

    Args:
        db (Session): The SQLAlchemy database session.
        id (int): The ID of the category to retrieve.

    Returns:
        Category: The Category object if found, otherwise None.
    """
    return db.query(model.Category).filter(model.Category.id == id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of categories from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[Category]: A list of Category objects.
    """
    return db.query(model.Category).offset(skip).limit(limit).all()


def get_subcategory(db: Session, name: str):
    """
    Retrieves a subcategory from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the subcategory to retrieve.

    Returns:
        SubCategory: The SubCategory object if found, otherwise None.
    """
    return db.query(model.SubCategory).filter(
        model.SubCategory.name == name).first()


def get_subcategory_by_id(db: Session, id: int):
    """
    Retrieves a subcategory from the database by its ID.

    Args:
        db (Session): The SQLAlchemy database session.
        id (int): The ID of the subcategory to retrieve.

    Returns:
        SubCategory: The SubCategory object if found, otherwise None.
    """
    return db.query(model.SubCategory).filter(
        model.SubCategory.id == id).first()


def get_subcategories(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of subcategories from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[SubCategory]: A list of SubCategory objects.
    """
    return db.query(model.SubCategory).offset(skip).limit(limit).all()


def get_article_type(db: Session, name: str):
    """
    Retrieves an article type from the database by its name.

    Args:
        db (Session): The SQLAlchemy database session.
        name (str): The name of the article type to retrieve.

    Returns:
        ArticleType: The ArticleType object if found, otherwise None.
    """
    return db.query(model.ArticleType).filter(
        model.ArticleType.name == name).first()


def get_article_types(db: Session, skip: int = 0, limit: int = 200):
    """
    Retrieves a list of article types from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[ArticleType]: A list of ArticleType objects.
    """
    return db.query(model.ArticleType).offset(skip).limit(limit).all()


def get_images(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of images from the database with pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[ImageProduct]: A list of ImageProduct objects.
    """
    return db.query(model.ImageProduct).offset(skip).limit(limit).all()


def get_images_and_categories(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves images along with their associated categories from the database.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        list[tuple]: A list of tuples containing image and category information.
    """
    return db.query(
                model.ImageProduct.id,
                model.ImageProduct.path,
                model.Gender.gender,
                model.Color.name.label('color'),
                model.Season.name.label('season'),
                model.ArticleType.name.label('article'),
                model.Category.name.label('category'),
                model.SubCategory.name.label('sub_category'),
                model.UsageType.name.label('usage_type')
                ).join(model.Gender, 
                        model.Gender.id == model.ImageProduct.id_gender
                ).join(model.Color, 
                        model.Color.id == model.ImageProduct.id_color
                ).join(model.Season, 
                        model.Season.id == model.ImageProduct.id_season
                ).join(model.ArticleType, 
                        model.ArticleType.id == model.ImageProduct.id_articletype
                ).join(model.SubCategory, 
                        model.SubCategory.id == model.ArticleType.id_subcategory
                ).join(model.Category, 
                        model.Category.id == model.SubCategory.id_category
                ).join(model.UsageType, 
                        model.UsageType.id == model.ImageProduct.id_usagetype
                ).offset(skip).limit(limit).all()


def create_color(db: Session, color: schema.Color):
    """
    Creates a new color entry in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        color (schema.Color): The Color schema object containing the color details.

    Returns:
        Color: The created Color object.
    """
    db_color = model.Color(name=color.name)
    db.add(db_color)
    db.commit()
    db.refresh(db_color)
    return db_color


def create_image_product(db: Session, 
                         image: schema.ImageProduct):
    """
    Creates a new image product entry in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        image (schema.ImageProduct): The ImageProduct schema object containing image details.

    Returns:
        ImageProduct: The created ImageProduct object.
    """
    db_image = model.ImageProduct(
        path=image.path,
        id_usagetype=image.id_usagetype,
        id_gender=image.id_gender,
        id_season=image.id_season,
        id_color=image.id_color,
        id_articletype=image.id_articletype,
        id_client=image.id_client)

    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_email(db: Session, email: str):
    return db.query(model.Client).filter(model.Client.email == email).first()


def create_client(db: Session, client=schema.CreateClient):
    db_client = model.Client(email=client.email,
                             password=hash_password(client.password))
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def client_authentication(db: Session, email: str, password: str):

    db_client = db.query(model.Client).filter(
        model.Client.email == email).first()

    if bcrypt.checkpw(password.encode('utf-8'),
                      db_client.password.encode('utf-8')):
        return db_client

    return False


def update_faceid(db: Session, id_client: int, faceid: str):
    db_client = db.query(model.Client).filter(
        model.Client.id == id_client).first()
    if not db_client:
        return False

    db_client.face_id = faceid
    db.commit()
    db.refresh(db_client)

    return True


def get_faceid(db: Session, id_client: int):
    db_client = db.query(model.Client.face_id).filter(
        model.Client.id == id_client).first()
    if not db_client:
        return False

    return db_client[0]
