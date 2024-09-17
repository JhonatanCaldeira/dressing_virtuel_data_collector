from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database import crud
from models import model
from schemas import schema

db = SessionLocal()


print(crud.get_images_and_categories(db, skip=0, limit=1))