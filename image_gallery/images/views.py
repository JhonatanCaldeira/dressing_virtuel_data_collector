from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Image

def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 20)  # 20 imagens por página

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'images/image_list.html', {'page_obj': page_obj})
