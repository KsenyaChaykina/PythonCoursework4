from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from sending_messages.models import Client, Message, Newsletter
from sending_messages.forms import ClientForm, MessageForm, NewsletterForm

""" ПО КЛИЕНТАМ """

# Список всех клиентов
class ClientListView(ListView):
    model = Client
    template_name = 'sending_messages/client_list.html'
    context_object_name = 'clients'

# Детальная информация о клиенте
class ClientDetailView(DetailView):
    model = Client
    template_name = 'sending_messages/client_detail.html'
    context_object_name = 'client'

# Добавление нового клиента
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'sending_messages/client_form.html'
    success_url = reverse_lazy('sending_messages:client_list')

# Редактирование данных клиента
class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'sending_messages/client_form.html'
    success_url = reverse_lazy('sending_messages:client_list')

# Удаление клиента
class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'sending_messages/client_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:client_list')

""" ПО СООБЩЕНИЯМ """

# Список всех сообщений
class MessageListView(ListView):
    model = Message
    template_name = 'sending_messages/message_list.html'
    context_object_name = 'messages'

# Просмотр конкретного сообщения
class MessageDetailView(DetailView):
    model = Message
    template_name = 'sending_messages/message_detail.html'
    context_object_name = 'msg'  # переименовано во избежание конфликта с системным messages в шаблонах

# Создание сообщения
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sending_messages/message_form.html'
    success_url = reverse_lazy('sending_messages:message_list')

# Редактирование сообщения
class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'sending_messages/message_form.html'
    success_url = reverse_lazy('sending_messages:message_list')

# Удаление сообщения
class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'sending_messages/message_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:message_list')

class BaseTemplateView(TemplateView):
    template_name = "sending_messages/base.html"

""" ПО РАССЫЛКАМ """


# Список всех рассылок с автообновлением статуса
class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'newsletter_list.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Пересчитываем статус для каждой рассылки перед выводом на экран
        for newsletter in queryset:
            newsletter.update_status()
        return queryset


# Просмотр одной рассылки
class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = 'newsletter_detail.html'
    context_object_name = 'newsletter'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # Пересчет и сохранение статуса при открытии страницы
        return obj


# Создание рассылки
class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'newsletter_form.html'
    success_url = reverse_lazy('newsletter_list')


# Редактирование рассылки
class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'newsletter_form.html'
    success_url = reverse_lazy('newsletter_list')


# Удаление рассылки
class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = 'newsletter_confirm_delete.html'
    success_url = reverse_lazy('newsletter_list')


# Отправка сообщений по требованию (кнопка в интерфейсе)
def send_newsletter_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    newsletter.update_status()

    # Проверка бизнес-логики: отправка разрешена только для запущенных рассылок
    if newsletter.status != 'Запущена':
        messages.error(request, f"Нельзя отправить рассылку. Текущий статус: {newsletter.status}")
        return redirect('newsletter_detail', pk=pk)

    emails = [client.email for client in newsletter.recipients.all()]

    if emails:
        try:
            send_mail(
                subject=newsletter.message.subject,
                message=newsletter.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=False,
            )
            messages.success(request, f"Рассылка успешно отправлена {len(emails)} получателям!")
        except Exception as e:
            messages.error(request, f"Ошибка при отправке почты: {e}")
    else:
        messages.warning(request, "У этой рассылки нет выбранных получателей.")

    return redirect('newsletter_detail', pk=pk)

