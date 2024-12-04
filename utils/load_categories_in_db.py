from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.model import ArticleType, Category, Color, Gender, ImageProduct, Season, SubCategory, UsageType, Base
from sqlalchemy_utils import database_exists, drop_database, create_database

import yaml
import pandas as pd

FASHION_DATASET_HOME = '/mnt/e/jhona/Documents/Estudo/AI Microsfot & Simplon.co/Projet_chef_doeuvre/fashion_dataset/fashion-dataset/'
dataset_file = 'styles.csv'


def load_config(filepath='config/config.yaml'):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config['database']

db_config = load_config()

connection = f"{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
engine = create_engine(f"postgresql://{connection}")

def recreate_db():
    if database_exists(engine.url):
        drop_database(engine.url)

    # Database creation
    create_database(engine.url)
    print("was it create? ", database_exists(engine.url))

    # Tables creation
    Base.metadata.create_all(engine)

def load_dataframe(df, header):
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
            print(item)
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

        print(new_item)
        session.add(new_item)

    session.commit()
    session.close()   

recreate_db()

headers = ['gender','masterCategory','subCategory','articleType','baseColour','season','usage']
#headers = ['usage']
# Load Dataframe
df = pd.read_csv(FASHION_DATASET_HOME + dataset_file, on_bad_lines='skip')

# Loop for each category to remove duplicate and store it in the DB
for header in headers:
    if header not in ['masterCategory','subCategory','articleType']:
        categories = list(set(df[header].dropna()))
    else:
        if header == 'masterCategory':
            df_filtred = df.query("(masterCategory == 'Apparel' or masterCategory == 'Accessories' or masterCategory == 'Footwear')")
            categories = list(set(df_filtred['masterCategory']))
        elif header == 'subCategory':
            df_filtred = df.query("(masterCategory == 'Apparel' or masterCategory == 'Accessories' or masterCategory == 'Footwear')")
            categories = df_filtred.groupby(['subCategory'])['masterCategory'].apply(lambda x: list(set(x))).reset_index().to_numpy()
        elif header == 'articleType':
            df_filtred = df.query("(masterCategory == 'Apparel' or masterCategory == 'Accessories' or masterCategory == 'Footwear')")
            categories = df_filtred.groupby(['articleType'])['subCategory'].apply(lambda x: list(set(x))).reset_index().to_numpy()
        else:
            continue
    load_dataframe(categories, header)

 

