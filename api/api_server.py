from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database import crud
from models import model
from schemas import schema

app = FastAPI()

# Dependancy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

PREFIX = 'dressing_virtuel'

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post(f"/{PREFIX}/colors/", response_model=schema.Color)
def create_color(color: schema.Color, db: Session = Depends(get_db)):
    db_color = crud.get_color(db, color.name)
    if db_color:
        raise HTTPException(status_code=400, detail="Color already registred.")
    return crud.create_color(db, color=color)

@app.get(f"/{PREFIX}/colors/", response_model=list[schema.Color])
def get_colors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    colors = crud.get_colors(db, skip=skip, limit=limit)
    return colors

@app.get(f"/{PREFIX}/seasons/", response_model=list[schema.Season])
def get_season(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    seasons = crud.get_seasons(db, skip=skip, limit=limit)
    return seasons

@app.get(f"/{PREFIX}/genders/", response_model=list[schema.Gender])
def get_genders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    genders = crud.get_genders(db, skip=skip, limit=limit)
    return genders

@app.get(f"/{PREFIX}/usage_types/", response_model=list[schema.UsageType])
def get_usage_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usage = crud.get_usage_types(db, skip=skip, limit=limit)
    return usage

@app.get(f"/{PREFIX}/categories/", response_model=list[schema.Category])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@app.get(f"/{PREFIX}/subcategories/", response_model=list[schema.SubCategory])
def get_subcategoriess(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    colors = crud.get_subcategories(db, skip=skip, limit=limit)
    return colors

@app.get(f"/{PREFIX}/article_types/", response_model=list[schema.ArticleType])
def get_article_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    colors = crud.get_article_types(db, skip=skip, limit=limit)
    return colors

@app.post(f"/{PREFIX}/import_image/", response_model=schema.ImageProduct)
def create_image_product( image:schema.ImageProduct, db: Session = Depends(get_db)):
    db_image = crud.create_image_product(db, image)
    return db_image