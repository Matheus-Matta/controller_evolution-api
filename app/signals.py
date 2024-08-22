from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_auth_user(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username=settings.DEFAULT_USER_USERNAME).exists():
        User.objects.create_superuser(
            username=settings.DEFAULT_USER_USERNAME,
            email=settings.DEFAULT_USER_EMAIL,
            password=settings.DEFAULT_USER_PASSWORD
        )