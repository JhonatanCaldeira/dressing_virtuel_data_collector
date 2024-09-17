from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('image_gallery', views.image_gallery, name='image_gallery'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Adiciona a configuração para servir as imagens externas
    urlpatterns += static(settings.EXTERNAL_IMAGES_URL, document_root=settings.EXTERNAL_IMAGES_ROOT)