from config import settings
from config.settings import CACHE_ENABLED
from sending_messages.models import Message, Client, Newsletter, MailingLog
from django.core.cache import cache
import smtplib
from django.core.mail import send_mail


def get_messages_from_cache():
    """ Получает данные из кеша, если кеш пуст, получает данные из бд и заисывает в кеш """
    if not CACHE_ENABLED:
        return Message.objects.all()
    key = 'message_list'
    messages = cache.get(key)
    if messages is not None:
        return messages
    messages = Message.objects.all()
    cache.set(key, messages)
    return messages


def get_clients_from_cache():
    """ Получает данные из кеша, если кеш пуст, получает данные из бд и заисывает в кеш """
    if not CACHE_ENABLED:
        return Client.objects.all()
    key = 'client_list'
    clients = cache.get(key)
    if clients is not None:
        return clients
    clients = Client.objects.all()
    cache.set(key, clients)
    return clients


def send_newsletter_mailing(newsletter_id):
    """
    Отправляет сообщения всем получателям конкретной рассылки
    и фиксирует попытки отправки в MailingLog.
    """
    try:
        newsletter = Newsletter.objects.get(pk=newsletter_id)
    except Newsletter.DoesNotExist:
        return f"Рассылка с ID {newsletter_id} не найдена."

    # Динамически обновляем статус рассылки на основе текущего времени
    newsletter.update_status()

    if newsletter.status != "Запущена":
        return f"Отмена отправки: текущий статус рассылки '{newsletter.status}'."

    # Получаем связанных клиентов и объект сообщения
    recipients = newsletter.recipients.all()
    message_obj = newsletter.message

    if not recipients.exists():
        return "У рассылки нет получателей."

    # Собираем список email-адресов
    recipient_emails = [client.email for client in recipients]

    # Инициализируем переменные для лога
    status = "success"
    server_response = "Письмо успешно отправлено всем получателям."

    try:
        # Отправляем одно письмо сразу всем скрытым или открытым списком получателей,
        # либо в цикле, если вам принципиальна индивидуальная отправка.
        # Для надежности массовой отправки используем встроенный send_mail.
        send_mail(
            subject=message_obj.subject,
            message=message_obj.body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_emails,
            fail_silently=False,
        )
    except smtplib.SMTPException as e:
        status = "failed"
        server_response = f"Ошибка SMTP: {str(e)}"
    except Exception as e:
        status = "failed"
        server_response = f"Непредвиденная ошибка сервера: {str(e)}"

    # Ключевое требование: Создаем запись о попытке (лог) после завершения отправки
    log = MailingLog.objects.create(
        status=status,
        server_response=server_response,
        mailing=newsletter
    )

    return f"Отправка завершена со статусом: {status}. Создан лог #{log.id}."
