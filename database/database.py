from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml

def load_config(filepath='config/config.yaml'):
    """
    Loads the database configuration from a YAML file.

    Args:
        filepath (str): Path to the YAML configuration file.

    Returns:
        dict: A dictionary containing the database configuration.
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['database']

# Load database configuration from the YAML file
db_config = load_config()

# Construct the database URL for SQLAlchemy
SQLALCHEMY_DATABASE_URL  = f"{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

# Create an SQLAlchemy engine for PostgreSQL
engine = create_engine(f"postgresql://{SQLALCHEMY_DATABASE_URL}")

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)