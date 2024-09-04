import os
import pandas as pd
from shutil import copyfile
from django.conf import settings
from images.models import Image

# Carregar o arquivo CSV
dataset_path = '/mnt/e/jhona/Documents/Estudo/AI Microsfot & Simplon.co/Projet_chef_doeuvre/clothing_dataset'

csv_file_path = dataset_path + '/images.csv'  # Substitua pelo caminho real do arquivo CSV
df = pd.read_csv(csv_file_path)

# Diretório de origem das imagens
source_dir = os.path.join(dataset_path, 'images_original')

# Diretório de destino das imagens
dest_dir = os.path.join(settings.MEDIA_ROOT, 'images')

# Garantir que o diretório de destino exista
os.makedirs(dest_dir, exist_ok=True)

# Filtrar as primeiras 10 imagens de cada categoria
categories = df['label'].unique()
images_to_import = []

for category in categories:
    category_images = df[df['label'] == category].head(10)
    images_to_import.append(category_images)

# Concatenar todas as imagens a serem importadas
images_to_import = pd.concat(images_to_import)

# Carregar as imagens para o Django
for _, row in images_to_import.iterrows():
    image_name = f"{row['image']}.jpg"
    source_path = os.path.join(source_dir, image_name)
    dest_path = os.path.join(dest_dir, image_name)
    
    if os.path.exists(source_path):
        # Copiar a imagem para o diretório de mídia
        copyfile(source_path, dest_path)
        
        # Criar uma instância do modelo Image
        image_instance = Image(
            category=row['label'],
            image=f"images/{image_name}"
        )
        
        # Salvar no banco de dados
        image_instance.save()

print("Importação concluída!")
