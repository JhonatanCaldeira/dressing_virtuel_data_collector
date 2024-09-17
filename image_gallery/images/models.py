from django.db import models

class Image(models.Model):
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return self.category

class ImageDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    gender = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    season = models.CharField(max_length=100)
    article = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)
    usage_type = models.CharField(max_length=100)