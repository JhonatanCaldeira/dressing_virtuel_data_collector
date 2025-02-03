from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.model import (ArticleType, 
                            Category, 
                            Color, 
                            Gender, 
                            Season, 
                            SubCategory, 
                            UsageType, 
                            Base)
from sqlalchemy_utils import database_exists, drop_database, create_database

import yaml
import pandas as pd

FASHION_DATASET_HOME = 'fashion_dataset/fashion-dataset/'
dataset_file = 'styles.csv'

def load_config(filepath='config/config.yaml'):
    """
    Load the database configuration from a YAML file.

    Args:
        filepath (str): Path to the YAML configuration file.

    Returns:
        dict: Database configuration dictionary with keys such as user, password, host, port, and dbname.
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['database']

db_config = load_config()

connection = f"{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
engine = create_engine(f"postgresql://{connection}")

def recreate_db():
    """
    Recreate the database by dropping it if it exists and then creating it again.
    Also creates all tables defined in the Base metadata.
    """
    if database_exists(engine.url):
        drop_database(engine.url)

    # Database creation
    create_database(engine.url)
    print("Database created?", database_exists(engine.url))

    # Tables creation
    Base.metadata.create_all(engine)

def clean_data(df):
    """
    Clean the dataset by performing the following operations:
    - Removing rows with missing or corrupted entries in essential columns.
    - Normalizing date formats and text formats.
    - Dropping any remaining rows with invalid or corrupted data.

    Args:
        df (pd.DataFrame): The dataset to be cleaned.

    Returns:
        pd.DataFrame: The cleaned dataset.
    """
    # Drop rows with missing essential columns
    essential_columns = ['gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season', 'usage']
    df = df.dropna(subset=essential_columns)

    # Normalize date formats (if applicable)
    if 'dateAdded' in df.columns:
        df['dateAdded'] = pd.to_datetime(df['dateAdded'], errors='coerce')

    # Homogenize text data (e.g., lowercase, remove extra spaces)
    for column in essential_columns:
        if column in df.columns:
            df[column] = df[column].str.strip().str.lower()

    # Remove entries with invalid or corrupted data
    df = df.dropna()  # Re-drop rows after normalization

    return df

def load_dataframe(df, header):
    """
    Load a specific category of data into the database.

    Args:
        df (list or ndarray): The data to be loaded.
        header (str): The header or category name (e.g., 'gender', 'baseColour').
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    for item in df:       
        if header == 'gender':
            new_item = Gender(
                gender = item
            )
        elif header == 'baseColour':
            new_item = Color(
                name = item
            )
        elif header == 'season':
            new_item = Season(
                name = item
            )
        elif header == 'usage':
            new_item = UsageType(
                name = item
            )
        elif header == 'masterCategory':
            new_item = Category(
                name = item
            )
        elif header == 'subCategory':
            query = session.query(
                Category.id
            ).filter_by(name = item[1][0]).first()

            if query is None:
                continue

            new_item = SubCategory(
                name = item[0],
                id_category = query[0]
            ) 
        elif header == 'articleType':
            query = session.query(
                SubCategory.id
            ).filter_by(name = item[1][0]).first()    

            if query is None:
                continue

            new_item = ArticleType(
                name = item[0],
                id_subcategory = query[0]
            )
            
        else:
            continue

        session.add(new_item)

    session.commit()
    session.close()   

recreate_db()

headers = ['gender','masterCategory','subCategory','articleType','baseColour','season','usage']

# Load and clean DataFrame
df = pd.read_csv(FASHION_DATASET_HOME + dataset_file, on_bad_lines='skip')
df = clean_data(df)

# Loop for each category to remove duplicates and store it in the DB
for header in headers:
    if header not in ['masterCategory','subCategory','articleType']:
        categories = list(set(df[header].dropna()))
    else:
        if header == 'masterCategory':
            df_filtered = df.query("(masterCategory == 'apparel' or masterCategory == 'accessories' or masterCategory == 'footwear')")
            categories = list(set(df_filtered['masterCategory']))
        elif header == 'subCategory':
            df_filtered = df.query("(masterCategory == 'apparel' or masterCategory == 'accessories' or masterCategory == 'footwear')")
            categories = df_filtered.groupby(['subCategory'])['masterCategory'].apply(lambda x: list(set(x))).reset_index().to_numpy()
        elif header == 'articleType':
            df_filtered = df.query("(masterCategory == 'apparel' or masterCategory == 'accessories' or masterCategory == 'footwear')")
            categories = df_filtered.groupby(['articleType'])['subCategory'].apply(lambda x: list(set(x))).reset_index().to_numpy()
        else:
            continue
    load_dataframe(categories, header)
