from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Image
from django.conf import settings
import requests

def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 50) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'images/image_list.html', {'page_obj': page_obj})

def image_gallery(request):
    api_url = "http://127.0.0.1:5000/dressing_virtuel/images_categories/?skip=0&limit=500"
    response = requests.get(api_url)

    if response.status_code == 200:
        images = response.json()

        # Ajustar o caminho das imagens para apontar para o diretório externo
        for image in images:
            image['path'] = image['path'].replace('/home/jcaldeira/dressing_virtuel_data_collector/image_scraper/images/full/', settings.EXTERNAL_IMAGES_URL)
    else:
        images = []  # Caso a API não esteja disponível.

    paginator = Paginator(images, 50)  # 50 imagens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'images/image_gallery.html', {'page_obj': page_obj})
