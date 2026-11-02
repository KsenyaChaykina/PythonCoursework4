from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from sending_messages.models import Client, Message, Newsletter
from sending_messages.forms import ClientForm, MessageForm, NewsletterForm
from sending_messages.services import send_newsletter_mailing

""" ПО КЛИЕНТАМ """


# Список всех клиентов
class ClientListView(ListView):
    model = Client
    template_name = "sending_messages/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Менеджеры видят ВСЕХ клиентов
        if user.groups.filter(name="Managers").exists() or user.is_staff:
            return queryset

        # Обычные пользователи видят ТОЛЬКО своих клиентов
        return queryset.filter(owner=user)


# Детальная информация о клиенте
class ClientDetailView(DetailView):
    model = Client
    template_name = "sending_messages/client_detail.html"
    context_object_name = "client"


# Добавление нового клиента
class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "sending_messages/client_form.html"
    success_url = reverse_lazy("sending_messages:client_list")

    def form_valid(self, form):
        # Привязываем текущего пользователя к сообщению
        form.instance.owner = self.request.user
        return super().form_valid(form)


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

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Менеджеры видят ВСЕ сообщения
        if user.groups.filter(name="Managers").exists() or user.is_staff:
            return queryset

        # Обычные пользователи видят ТОЛЬКО свои сообщения
        return queryset.filter(owner=user)


# Просмотр конкретного сообщения
class MessageDetailView(DetailView):
    model = Message
    template_name = "sending_messages/message_detail.html"
    context_object_name = "msg"  # переименовано во избежание конфликта с системным messages в шаблонах


# Создание сообщения
class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "sending_messages/message_form.html"
    success_url = reverse_lazy("sending_messages:message_list")

    def form_valid(self, form):
        # Привязываем текущего пользователя к сообщению
        form.instance.owner = self.request.user
        return super().form_valid(form)


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


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = "sending_messages/newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Менеджеры видят ВСЕ рассылки
        if user.groups.filter(name="Managers").exists() or user.is_staff:
            return queryset

        # Обычные пользователи видят ТОЛЬКО свои
        return queryset.filter(owner=user)


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = "sending_messages/newsletter_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "sending_messages/newsletter_form.html"
    success_url = reverse_lazy("sending_messages:newsletter_list")

    def form_valid(self, form):
        # Автоматически назначаем текущего пользователя владельцем рассылки
        form.instance = form.save(commit=False)
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "sending_messages/newsletter_form.html"
    success_url = reverse_lazy("sending_messages:newsletter_list")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Менеджер может отключать чужие рассылки
        if self.request.user.has_perm("mailing.can_disable_mailing"):
            return queryset

        # Обычный владелец может редактировать только свою рассылку
        return queryset.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)

        # Защитная проверка: если обычный юзер пытается зайти в чужой объект
        if self.object.owner != self.request.user and not self.request.user.has_perm("mailing.can_disable_mailing"):
            raise PermissionDenied("Вы не являетесь владельцем этой рассылки.")

        return self.object


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


class TriggerNewsletterView(View):
    """ Контроллер для ручного или триггерного запуска отправки рассылки """

    def post(self, request, pk):
        # Проверяем существование рассылки
        newsletter = get_object_or_404(Newsletter, pk=pk)

        # Передаем ID рассылки в сервисный слой
        result_message = send_newsletter_mailing(newsletter.id)

        # Выводим пользователю системное push-уведомление с результатом
        messages.info(request, result_message)

        # Перенаправляем обратно на страницу рассылки (замените 'newsletter_detail' на ваш URL-name)
        return redirect('sending_messages/newsletter_detail', pk=pk)
