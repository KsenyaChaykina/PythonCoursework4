from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from config import settings


class Mailing(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        permissions = [
            ("can_view_all_mailings", "Может просматривать любые рассылки"),
            ("can_disable_mailing", "Может отключать рассылки"),
        ]


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("Email адрес", unique=True)
    is_verified = models.BooleanField("Подтвержден", default=False)

    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_block_users", "Может блокировать пользователей сервиса"),
        ]

    def __str__(self):
        return self.email
