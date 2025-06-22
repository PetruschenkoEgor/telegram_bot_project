from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(verbose_name="Ник", unique=True)
    email = None

    # Аутентификация будет по email
    USERNAME_FIELD = "username"
    # Список обязательных для заполнения полей
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
