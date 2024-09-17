from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database import crud
from models import model
from schemas import schema

# Initialize the FastAPI app
app = FastAPI()

# Dependency to get a database session for each request
def get_db():
    """
    Provides a database session to interact with the database during the request lifecycle.
    Closes the session after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Ensure the session is closed after use

# Prefix used for routing in the application
PREFIX = 'dressing_virtuel'

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}

@app.post(f"/{PREFIX}/colors/", response_model=schema.Color)
def create_color(color: schema.Color, db: Session = Depends(get_db)):
    """
    Create a new color entry in the database.
    
    - If the color already exists, raises an HTTP 400 error.
    - Returns the created color.
    """
    db_color = crud.get_color(db, color.name)
    if db_color:
        raise HTTPException(status_code=400, detail="Color already registred.")
    return crud.create_color(db, color=color)

@app.get(f"/{PREFIX}/colors/", response_model=list[schema.Color])
def get_colors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of colors from the database.
    
    - Supports pagination with `skip` and `limit` parameters.
    - Returns a list of colors.
    """
    colors = crud.get_colors(db, skip=skip, limit=limit)
    return colors

@app.get(f"/{PREFIX}/seasons/", response_model=list[schema.Season])
def get_season(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of seasons from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of seasons.
    """
    seasons = crud.get_seasons(db, skip=skip, limit=limit)
    return seasons

@app.get(f"/{PREFIX}/genders/", response_model=list[schema.Gender])
def get_genders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of genders from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of genders.
    """
    genders = crud.get_genders(db, skip=skip, limit=limit)
    return genders

@app.get(f"/{PREFIX}/usage_types/", response_model=list[schema.UsageType])
def get_usage_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of usage types from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of usage types.
    """
    usage = crud.get_usage_types(db, skip=skip, limit=limit)
    return usage

@app.get(f"/{PREFIX}/categories/", response_model=list[schema.Category])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of categories from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of categories.
    """
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@app.get(f"/{PREFIX}/subcategories/", response_model=list[schema.SubCategory])
def get_subcategoriess(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of subcategories from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of subcategories.
    """
    colors = crud.get_subcategories(db, skip=skip, limit=limit)
    return colors

@app.get(f"/{PREFIX}/article_types/", response_model=list[schema.ArticleType])
def get_article_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of article types from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of article types.
    """
    colors = crud.get_article_types(db, skip=skip, limit=limit)
    return colors

@app.post(f"/{PREFIX}/import_image/", response_model=schema.ImageProduct)
def create_image_product( image:schema.ImageProduct, db: Session = Depends(get_db)):
    """
    Create a new image product entry in the database.
    
    - Returns the created image product.
    """
    db_image = crud.create_image_product(db, image)
    return db_image

@app.get(f"/{PREFIX}/images_categories/", response_model=list[schema.ImageProductDetailed])
def get_all_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all images along with their categories from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a detailed list of images and categories.
    """
    images = crud.get_images_and_categories(db, skip=skip, limit=limit)
    return images

@app.get(f"/{PREFIX}/images/", response_model=list[schema.ImageProduct])
def get_all_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all images from the database.
    
    - Supports pagination with `skip` and `limit`.
    - Returns a list of images.
    """
    images = crud.get_images(db, skip=skip, limit=limit)
    return images