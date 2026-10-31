from config.settings import CACHE_ENABLED
from sending_messages.models import Message, Client
from django.core.cache import cache


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
