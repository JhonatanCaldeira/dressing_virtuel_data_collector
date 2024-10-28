from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database import crud
from models import model
from schemas import schema
import uvicorn
import yaml

def load_config(filepath='config/config.yaml'):
    """
    Loads the webservice configuration from a YAML file.

    Args:
        filepath (str): Path to the YAML configuration file.

    Returns:
        dict: A dictionary containing the database configuration.
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['webservice_server_postgre']

# Load database configuration from the YAML file
ws_config = load_config()

# Prefix used for routing in the application
# PREFIX = 'dressing_virtuel'
PREFIX = ws_config['prefix']
PORT = ws_config['port']

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
def create_image_product(image:schema.ImageProduct, db: Session = Depends(get_db)):
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

@app.post(f"/{PREFIX}/create_client/", response_model=schema.CreateClientResp)
def create_client(client: schema.CreateClient, db: Session = Depends(get_db)):
    """
    Create a new client entry in the database.
    
    - If the email already exists, raises an HTTP 400 error.
    - Returns the created id.
    """
    client_email = crud.get_email(db, client.email)
    if client_email:
        raise HTTPException(status_code=400, detail="Email already registred.")
    
    db_client = crud.create_client(db, client=client)
    if db_client:
        return {"status":1, "message":'User created successfully'}
    
    return {"status":0, "message":'Error in the user creation'}

@app.get(f"/{PREFIX}/authentication/", response_model=schema.ClientAuthResp)
def authentication(email: str, password: str, db: Session = Depends(get_db)):

    client_auth = crud.client_authentication(db, email, password)

    if not client_auth:
        raise HTTPException(status_code=400, detail="Invalid user or password.")
    
    return {"id":client_auth.id, "email":client_auth.email}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)