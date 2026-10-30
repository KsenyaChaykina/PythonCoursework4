from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView

from users.forms import UserRegisterForm
from users.models import CustomUser
from config.settings import EMAIL_HOST_USER

import secrets

from django.contrib.auth.forms import SetPasswordForm
from django.views.generic import FormView
from django import forms
from django.contrib import messages


class UserCreateView(CreateView):
    model = CustomUser
    template_name = "users/user_form.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse_lazy("users:login"))


# Дополнительная простая форма для ввода Email (можно вынести в forms.py)
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Ваш Email", widget=forms.EmailInput(attrs={"class": "form-control"}))


# Шаг 1: Запрос на восстановление пароля
class PasswordResetRequestView(FormView):
    template_name = "users/password_reset_request.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        # Ищем пользователя. Если не нашли, тихо редиректим (в целях безопасности)
        user = CustomUser.objects.filter(email=email).first()

        if user:
            # Генерируем новый токен для сброса пароля
            token = secrets.token_hex(16)
            user.token = token  # Используем существующее поле token
            user.save()

            host = self.request.get_host()
            url = f"http://{host}/password-reset-confirm/{token}/"

            send_mail(
                subject="Восстановление пароля",
                message=f"Привет! Для сброса пароля перейди по ссылке: {url}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
            messages.success(self.request, "Ссылка для смены пароля отправлена на ваш email.")
        else:
            messages.info(self.request, "Если данный email зарегистрирован, на него отправлено письмо.")

        return super().form_valid(form)


# Шаг 2: Страница ввода нового пароля при переходе по ссылке
class PasswordResetConfirmView(FormView):
    template_name = "users/password_reset_confirm.html"
    form_class = SetPasswordForm  # Встроенная форма Django для установки пароля без старого
    success_url = reverse_lazy("users:login")

    def get_form_kwargs(self):
        # SetPasswordForm требует объект пользователя в качестве первого аргумента kwargs['user']
        kwargs = super().get_form_kwargs()
        token = self.kwargs.get("token")
        self.user = get_object_or_404(CustomUser, token=token)
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        # Сохраняем новый пароль (Django сам его захеширует)
        form.save()

        # Очищаем токен, чтобы ссылку нельзя было использовать повторно
        self.user.token = None
        self.user.save()

        messages.success(self.request, "Пароль успешно изменен. Теперь вы можете войти.")
        return super().form_valid(form)
