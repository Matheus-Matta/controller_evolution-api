from django.db import models
from django.contrib.auth.models import User

class Instance(models.Model):
    instance_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    public_name = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    integration_type = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
 
    def __str__(self):
        return self.public_name

