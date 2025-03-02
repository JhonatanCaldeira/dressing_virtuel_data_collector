from fastapi import Depends, FastAPI, HTTPException, Security, UploadFile, File, Form
from fastapi.security.api_key import APIKey, APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from typing import Annotated
from api.prometheus_metrics import PrometheusMetrics
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session
from database.connection import SessionLocal, engine
from database import crud
from schemas import schema
import os
import base64

PREFIX = os.getenv("PG_API_ENDPONT")
API_KEY = os.getenv("PG_API_KEY")

# Initialize the FastAPI app
app = FastAPI()
#Instrumentator().instrument(app).expose(app)
metrics = PrometheusMetrics()
metrics.setup(app)

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Retrieves the API Key from the request headers.

    Args:
    api_key_header (str): The API Key from the request headers.

    Returns:
    str: The API Key if it matches the expected value.

    Raises:
    HTTPException: If the API Key does not match the expected value.
    """
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )

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
        db.close()  # Ensure the session is closed after use


@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}


@app.post(f"/{PREFIX}/colors/", response_model=schema.Color)
def create_color(color: schema.Color,
                 db: Session = Depends(get_db),
                 api_key: APIKey = Depends(get_api_key)):
    """
    Endpoint to create a new color entry in the database.

    Args:
        color (schema.Color): The Color schema object containing the color details.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        schema.Color: The created color object.

    Raises:
        HTTPException: If the color already exists, raises an HTTP 400 error.
    """
    # Check if the color already exists in the database
    db_color = crud.get_color(db, color.name)
    if db_color:
        # Raise an error if the color is already registered
        raise HTTPException(status_code=400, detail="Color already registred.")
    
    # Create and return the new color entry
    return crud.create_color(db, color=color)


@app.get(f"/{PREFIX}/colors/", response_model=list[schema.Color])
def get_colors(skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db),
               api_key: APIKey = Depends(get_api_key)):
    """
    Retrieve a list of colors from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the color list, and the `limit` parameter determines the
    maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[Color]: A list of Color objects.
    """
    colors = crud.get_colors(db, skip=skip, limit=limit)
    return colors


@app.get(f"/{PREFIX}/seasons/", response_model=list[schema.Season])
def get_seasons(skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db),
                api_key: APIKey = Depends(get_api_key)) -> list[schema.Season]:
    """
    Retrieve a list of seasons from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the season list, and the `limit` parameter determines the
    maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[Season]: A list of Season objects.
    """
    seasons = crud.get_seasons(db, skip=skip, limit=limit)
    return seasons


@app.get(f"/{PREFIX}/genders/", response_model=list[schema.Gender])
def get_genders(skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db),
                api_key: APIKey = Depends(get_api_key)) -> list[schema.Gender]:
    """
    Retrieve a list of genders from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the gender list, and the `limit` parameter determines the
    maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[Gender]: A list of Gender objects.
    """
    genders = crud.get_genders(db, skip=skip, limit=limit)
    return genders


@app.get(f"/{PREFIX}/usage_types/", response_model=list[schema.UsageType])
def get_usage_types(skip: int = 0, limit: int = 100,
                    db: Session = Depends(get_db),
                    api_key: APIKey = Depends(get_api_key)) -> list[schema.UsageType]:
    """
    Retrieve a list of usage types from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the usage type list, and the `limit` parameter determines the
    maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[UsageType]: A list of UsageType objects.
    """
    usage = crud.get_usage_types(db, skip=skip, limit=limit)
    return usage


@app.get(f"/{PREFIX}/categories/", response_model=list[schema.Category])
def get_categories(skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db),
                   api_key: APIKey = Depends(get_api_key)) -> list[schema.Category]:
    """
    Retrieve a list of categories from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the category list, and the `limit` parameter determines the
    maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[schema.Category]: A list of Category objects.
    """
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@app.get(f"/{PREFIX}/subcategories/", response_model=list[schema.SubCategory])
def get_subcategories(skip: int = 0, limit: int = 100,
                      db: Session = Depends(get_db),
                      api_key: APIKey = Depends(get_api_key)):
    """
    Retrieve a list of subcategories from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the subcategory list, and the `limit` parameter determines
    the maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[SubCategory]: A list of SubCategory objects.
    """
    # Query the database for subcategories with pagination
    subcategories = crud.get_subcategories(db, skip=skip, limit=limit)
    
    # Return the list of subcategories
    return subcategories


@app.get(f"/{PREFIX}/article_types/", response_model=list[schema.ArticleType])
def get_article_types(skip: int = 0, limit: int = 100,
                      db: Session = Depends(get_db),
                      api_key: APIKey = Depends(get_api_key)):
    """
    Retrieve a list of article types from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the article type list, and the `limit` parameter determines
    the maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[ArticleType]: A list of ArticleType objects.
    """
    article_types = crud.get_article_types(db, skip=skip, limit=limit)
    return article_types

@app.get(f"/{PREFIX}/article_types_by_category/", response_model=list[schema.ArticleType])
def get_article_types_by_category(category_id: int, skip: int = 0, limit: int = 100,
                      db: Session = Depends(get_db),
                      api_key: APIKey = Depends(get_api_key)):
    """
    Retrieve a list of article types from the database.
    Args:
        category_id (int): The ID of the category to retrieve article types for.
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[ArticleType]: A list of ArticleType objects.
    """
    article_types = crud.get_article_types_by_categories(db,
                                                         category_id=category_id, 
                                                         skip=skip, 
                                                         limit=limit)
    return article_types


@app.post(f"/{PREFIX}/import_image/", response_model=schema.ImageProduct)
def create_image_product(image: schema.ImageProduct,
                         db: Session = Depends(get_db),
                         api_key: APIKey = Depends(get_api_key)):
    """
    Creates a new image product entry in the database.

    Args:
        image (schema.ImageProduct): The ImageProduct schema object containing image details.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        ImageProduct: The created ImageProduct object.
    """
    # Create a new image product entry in the database
    db_image = crud.create_image_product(db, image)
    # Return the created image product
    return db_image


@app.get(f"/{PREFIX}/images_categories/", response_model=list[schema.ImageProductDetailed])
def get_all_images(skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db),
                   api_key: APIKey = Depends(get_api_key)):
    """
    Retrieve a list of all images along with their categories from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the image and category list, and the `limit` parameter
    determines the maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[ImageProductDetailed]: A list of ImageProductDetailed objects.
    """
    # Retrieve a list of all images along with their categories from the database
    images = crud.get_images_and_categories(db, skip=skip, limit=limit)
    # Return the detailed list of images and categories
    return images


@app.get(f"/{PREFIX}/images/", response_model=list[schema.ImageProduct])
def get_all_images(skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db),
                   api_key: APIKey = Depends(get_api_key)):
    """
    Retrieve a list of all images from the database.

    This endpoint supports pagination by providing the `skip` and `limit`
    parameters. The `skip` parameter determines the number of records to skip
    before returning the image list, and the `limit` parameter determines the
    maximum number of records to return.

    Args:
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        db (Session): The SQLAlchemy database session.
        api_key (APIKey): The API Key for authentication.

    Returns:
        list[ImageProduct]: A list of ImageProduct objects.
    """
    images = crud.get_images(db, skip=skip, limit=limit)
    # Return the list of images
    return images


@app.post(f"/{PREFIX}/create_client/", response_model=schema.CreateClientResp)
def create_client(client: schema.CreateClient,
                  db: Session = Depends(get_db),
                  api_key: APIKey = Depends(get_api_key)):
    """
    Creates a new client entry in the database.

    Args:
        client (schema.CreateClient): The CreateClient schema object containing the client details.

    Returns:
        CreateClientResp: A CreateClientResp object indicating the creation status.

    Raises:
        HTTPException: If the email already exists, raises an HTTP 400 error.
    """
    client_email = crud.get_email(db, client.email)
    if client_email:
        raise HTTPException(status_code=400, detail="Email already registred.")

    db_client = crud.create_client(db, client=client)
    if db_client:
        # Return a success message
        return {"status": 1, "message": 'User created successfully'}

    # Return an error message
    return {"status": 0, "message": 'Error in the user creation'}


@app.get(f"/{PREFIX}/authentication/", response_model=schema.ClientAuthResp)
def authentication(email: str, password: str,
                   db: Session = Depends(get_db),
                   api_key: APIKey = Depends(get_api_key)) -> schema.ClientAuthResp:
    """
    Authenticates a user based on the email and password provided.

    Args:
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        ClientAuthResp: A ClientAuthResp object containing the authenticated user's ID and email.

    Raises:
        HTTPException: If the user is not found or the password is invalid, raises an HTTP 400 error.
    """
    client_auth = crud.client_authentication(db, email, password)

    if not client_auth:
        raise HTTPException(
            status_code=400, detail="Invalid user or password.")

    return {"id": client_auth.id, "email": client_auth.email}


@app.post(f"/{PREFIX}/upload_faceid/")
def update_faceid(id_client: Annotated[int, Form()],
                  image: UploadFile = File(...),
                  db: Session = Depends(get_db),
                  api_key: APIKey = Depends(get_api_key)):
    """
    Endpoint to update the FaceID of a client.

    Args:
        id_client (int): The ID of the client whose FaceID is being updated.
        image (UploadFile): The uploaded image file containing the new FaceID.
        db (Session): Database session dependency.
        api_key (APIKey): API key dependency for security.

    Returns:
        dict: A dictionary containing the status of the operation.

    Raises:
        HTTPException: If the FaceID update fails, an HTTP 400 error is raised.
    """
    # Read the image bytes from the uploaded file
    image_bytes = image.file.read()
    
    # Convert the image bytes to a base64 encoded string
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Update the FaceID in the database
    if not crud.update_faceid(db, id_client, image_base64):
        raise HTTPException(status_code=400, detail="Invalid Image.")

    # Return a success status
    return {"status": "success"}


@app.get(f"/{PREFIX}/get_faceid")
def get_faceid(id_client: int,
               db: Session = Depends(get_db),
               api_key: APIKey = Depends(get_api_key)) -> dict:
    """
    Retrieves the FaceID of a client from the database.

    Args:
        id_client (int): The ID of the client whose FaceID is being requested.
        db (Session): The database session dependency.
        api_key (APIKey): The API key dependency for security.

    Returns:
        dict: A dictionary containing the FaceID as a base64 encoded string.

    Raises:
        HTTPException: If the FaceID is not found, an HTTP 404 error is raised.
    """
    # Retrieve the FaceID from the database
    db_faceid = crud.get_faceid(db, id_client)
    if not db_faceid:
        # Raise an HTTP 404 error if the FaceID is not found
        raise HTTPException(status_code=404, detail="FaceId not found.")

    # Return the FaceID as a base64 encoded string
    return {'images': db_faceid.tobytes().decode("utf-8")}

@app.get(f"/{PREFIX}/images_from_client/", response_model=list[schema.ImageProductDetailed])
def get_images_from_client(
        skip: int = 0,  # The number of records to skip (for pagination)
        limit: int = 100,  # The maximum number of records to return
        client_id: int = 0,  # The ID of the client whose images are being requested
        db: Session = Depends(get_db),  # The database session dependency
        api_key: APIKey = Depends(get_api_key)  # The API key dependency for security
) -> list[schema.ImageProductDetailed]:
    """
    Retrieves a list of images from the database associated with a client.

    Args:
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.
        client_id (int): The ID of the client whose images are being requested.
        db (Session): The database session dependency.
        api_key (APIKey): The API key dependency for security.

    Returns:
        list[ImageProductDetailed]: A list of ImageProductDetailed objects.

    Raises:
        HTTPException: If the client ID is invalid, an HTTP 404 error is raised.
    """
    # Retrieve the images from the database
    images_from_client = crud.get_images_from_user(db, skip=skip, limit=limit, 
                                                   client_id=client_id)
    if not images_from_client:
        # Raise an HTTP 404 error if the client ID is invalid
        raise HTTPException(status_code=404, detail="Client ID is invalid.")

    # Return the list of images
    return images_from_client
