from django import forms
from django.forms import ModelForm, BooleanField

from sending_messages.models import Client, Message, Newsletter


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs['class'] = 'form-check-input'
            else:
                fild.widget.attrs['class'] = 'form-control'


class ClientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Client
        fields = ['full_name', 'email', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Дополнительная информация...'}),
        }


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите тему письма'}),
            'body': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Введите текст сообщения'}),
        }


class NewsletterForm(StyleFormMixin, ModelForm):
    # Поля с множественным выбором клиентов в виде чекбоксов
    recipients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Получатели"
    )

    # Выпадающий список для выбора заранее созданного сообщения
    message = forms.ModelChoiceField(
        queryset=Message.objects.all(),
        empty_label="Выберите сообщение из списка",
        label="Сообщение"
    )

    class Meta:
        model = Newsletter
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
