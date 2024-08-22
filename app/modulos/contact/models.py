from django.db import models
from django.contrib.auth.models import User
from app.modulos.instance.models import Instance
from app.modulos.tags.models import Tag

class Contact(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.SET_NULL, related_name='contacts', null=True, blank=True)
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    tags = models.ManyToManyField('tags.Tag', related_name='contacts', blank=True)

    def __str__(self):
        return self.name

