from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from sending_messages.models import Client, Message, Newsletter
from sending_messages.forms import ClientForm, MessageForm, NewsletterForm

""" ПО КЛИЕНТАМ """


# Список всех клиентов
class ClientListView(ListView):
    model = Client
    template_name = "sending_messages/client_list.html"
    context_object_name = "clients"


# Детальная информация о клиенте
class ClientDetailView(DetailView):
    model = Client
    template_name = "sending_messages/client_detail.html"
    context_object_name = "client"


# Добавление нового клиента
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "sending_messages/client_form.html"
    success_url = reverse_lazy("sending_messages:client_list")


# Редактирование данных клиента
class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "sending_messages/client_form.html"
    success_url = reverse_lazy("sending_messages:client_list")


# Удаление клиента
class ClientDeleteView(DeleteView):
    model = Client
    template_name = "sending_messages/client_confirm_delete.html"
    success_url = reverse_lazy("sending_messages:client_list")


""" ПО СООБЩЕНИЯМ """


# Список всех сообщений
class MessageListView(ListView):
    model = Message
    template_name = "sending_messages/message_list.html"
    context_object_name = "messages"


# Просмотр конкретного сообщения
class MessageDetailView(DetailView):
    model = Message
    template_name = "sending_messages/message_detail.html"
    context_object_name = "msg"  # переименовано во избежание конфликта с системным messages в шаблонах


# Создание сообщения
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "sending_messages/message_form.html"
    success_url = reverse_lazy("sending_messages:message_list")


# Редактирование сообщения
class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "sending_messages/message_form.html"
    success_url = reverse_lazy("sending_messages:message_list")


# Удаление сообщения
class MessageDeleteView(DeleteView):
    model = Message
    template_name = "sending_messages/message_confirm_delete.html"
    success_url = reverse_lazy("sending_messages:message_list")


class BaseTemplateView(TemplateView):
    template_name = "sending_messages/base.html"


class MainPageView(TemplateView):
    template_name = "sending_messages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # 1. Общее количество всех созданных рассылок
        context["total_newsletters"] = Newsletter.objects.count()

        # 2. Количество активных рассылок (время внутри интервала + статус 'Запущена')
        context["active_newsletters"] = Newsletter.objects.filter(
            start_time__lte=now, end_time__gte=now, status="Запущена"
        ).count()

        # 3. Количество уникальных получателей (все клиенты в системе)
        context["total_clients"] = Client.objects.count()

        return context


""" ПО РАССЫЛКАМ """


class NewsletterListView(ListView):
    model = Newsletter
    template_name = "sending_messages/newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        queryset = super().get_queryset()
        for newsletter in queryset:
            newsletter.update_status()
        return queryset


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = "sending_messages/newsletter_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "sending_messages/newsletter_form.html"
    success_url = reverse_lazy("sending_messages:newsletter_list")


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "sending_messages/newsletter_form.html"
    success_url = reverse_lazy("sending_messages:newsletter_list")


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = "sending_messages/newsletter_confirm_delete.html"
    success_url = reverse_lazy("sending_messages:newsletter_list")


def newsletter_create(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sending_messages:newsletter_list")
    else:
        form = NewsletterForm()

    return render(request, "sending_messages/newsletter_form.html", {"form": form})
