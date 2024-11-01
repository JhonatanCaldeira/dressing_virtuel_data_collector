from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

HOST = os.getenv("PG_DB_HOST")
USER = os.getenv("PG_DB_USER")
PORT = os.getenv("PG_DB_PORT")
DB_NAME = os.getenv("PG_DB_NAME")
PASSWORD = os.getenv("PG_DB_PASSWORD")

# Construct the database URL for SQLAlchemy
SQLALCHEMY_DATABASE_URL  = f"{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# Create an SQLAlchemy engine for PostgreSQL
engine = create_engine(f"postgresql://{SQLALCHEMY_DATABASE_URL}")

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)