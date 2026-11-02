from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from config import settings


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Введите ваш Email")
    full_name = models.CharField(
        max_length=255, verbose_name="Ф. И. О.", help_text="Введите ваши Фамилию, Имя, Отчество"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий", help_text="Оставьте комментарий")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма", help_text="Введите тему письма")
    body = models.TextField(verbose_name="Тело письма", help_text="Напишите письмо")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


class Newsletter(models.Model):
    STATUS_CHOICES = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Создана", verbose_name="Статус")
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="newsletters", verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(Client, related_name="newsletters", verbose_name="Получатели")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка #{self.pk} (Тема: {self.message.subject})"

    def update_status(self):
        """Проверяет текущее время и обновляет статус в БД, если он изменился"""
        now = timezone.now()
        new_status = "Создана"

        if now < self.start_time:
            new_status = "Создана"
        elif self.start_time <= now <= self.end_time:
            new_status = "Запущена"
        else:
            new_status = "Завершена"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    def clean(self):
        super().clean()
        now = timezone.now()
        if not self.pk and self.start_time and self.start_time < now:
            raise ValidationError({"start_time": "Дата и время начала отправки не могут быть в прошлом!"})
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "Дата окончания должна быть строго позже даты начала отправки!"})


class MailingLog(models.Model):
    """Модель попытки отправки рассылки"""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Ошибка"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время последней попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус попытки")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ почтового сервера")
    mailing = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name="logs", verbose_name="Рассылка")

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"

    def __str__(self):
        return f"Лог {self.id} для рассылки {self.mailing_id} ({self.status})"
