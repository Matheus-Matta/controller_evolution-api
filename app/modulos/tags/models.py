from django.db import models
from django.contrib.auth.models import User
from app.modulos.instance.models import Instance

class Tag(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name