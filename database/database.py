from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml

def load_config(filepath='config/config.yaml'):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['database']

db_config = load_config()

SQLALCHEMY_DATABASE_URL  = f"{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
engine = create_engine(f"postgresql://{SQLALCHEMY_DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)