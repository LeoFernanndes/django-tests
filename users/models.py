from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):

    def create(self, *args, **kwargs):
        return super().create_user(*args, **kwargs)


class User(AbstractUser):
    
    objects = CustomUserManager()