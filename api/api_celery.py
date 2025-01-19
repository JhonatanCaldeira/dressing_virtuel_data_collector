from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    Security
)
from api.prometheus_metrics import PrometheusMetrics
from fastapi.security.api_key import APIKey, APIKeyHeader
from schemas.schema import CeleryImageClassification, CelerySuggestion
from logger.logging_config import setup_logging
from broker import tasks
import os

logger = setup_logging(__name__)

PREFIX = os.getenv("CELERY_API_ENDPONT")
API_KEY = os.getenv("CELERY_API_KEY")
TEMP_DIR = os.getenv("IMAGE_TMP_DIR")

app = FastAPI()
metrics = PrometheusMetrics()
metrics.setup(app)

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        logger.error(f"Could not validate API KEY")
        raise HTTPException(
            status_code=403, 
            detail="Could not validate API KEY"
        )
    
@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    logger.info("Celery API its alive")

    return {"message": "I'm alive!"}

@app.post(f"/{PREFIX}/task_image_classification")
async def task_image_classification(request: CeleryImageClassification,
                                    api_key: APIKey = Depends(get_api_key)):
    logger.info("Starting task_image_classification")
    
    tasks.identify_clothes(request.id, request.images)
    
    logger.info("Finished task_image_classification")
    
    return True

@app.get(f"/{PREFIX}/get_suggestions")
async def get_suggestions(request: CelerySuggestion,
                          api_key: APIKey = Depends(get_api_key)):
    logger.info("Starting get_suggestions")
    logger.info("Getting Lat and Long from Address")

    response = tasks.get_lat_long(request.address)

    if response is None:
        raise HTTPException(
            status_code=403, 
            detail="Could not get Latitude and Longitude"
        )

    datetime = request.date + 'T12:00:00Z'
    lat = response['lat']
    long = response['long']

    logger.info("Getting Meteo")
    response = tasks.get_meteo(datetime,lat,long)

    if response is None:
        raise HTTPException(
            status_code=403, 
            detail="Could not get Meteo data"
        )

    return response