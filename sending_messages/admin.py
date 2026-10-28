from django.contrib import admin

from sending_messages.models import Client, Message, Newsletter


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject')

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status')
    list_filter = ('status',)
    search_fields = ('start_time', 'end_time', 'status')

