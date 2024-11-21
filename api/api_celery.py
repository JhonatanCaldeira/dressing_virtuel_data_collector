from fastapi import (
    Depends, 
    FastAPI, 
    HTTPException, 
    Security
)
from fastapi.security.api_key import APIKey, APIKeyHeader
from broker import tasks
from schemas.schema import CeleryImageClassification
import os

PREFIX = os.getenv("CELERY_API_ENDPONT")
API_KEY = os.getenv("CELERY_API_KEY")
TEMP_DIR = os.getenv("IMAGE_TMP_DIR")

app = FastAPI()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, 
            detail="Could not validate API KEY"
        )
    
@app.get("/")
async def root():
    """
    Root endpoint that returns a simple message.
    """
    return {"message": "I'm alive!"}

@app.post(f"/{PREFIX}/task_image_classification")
async def task_image_classification(request: CeleryImageClassification,
                                    api_key: APIKey = Depends(get_api_key)):
    
    tasks.identify_clothes(request.id, request.images)

    return True