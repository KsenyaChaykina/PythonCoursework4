from sending_messages.apps import SendingMessagesConfig
from django.urls import path
from sending_messages.views import (
    ClientListView,
    ClientDetailView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    MessageListView,
    MessageDetailView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    BaseTemplateView,
    NewsletterListView,
    NewsletterDetailView,
    NewsletterCreateView,
    NewsletterUpdateView,
    NewsletterDeleteView,
    MainPageView,
)

app_name = SendingMessagesConfig.name

urlpatterns = [
    path("", BaseTemplateView.as_view(), name="base"),
    path("index/", MainPageView.as_view(), name="index"),
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/new/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/new/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("newsletter/", NewsletterListView.as_view(), name="newsletter_list"),
    path("newsletter/<int:pk>/", NewsletterDetailView.as_view(), name="newsletter_detail"),
    path("newsletter/new/", NewsletterCreateView.as_view(), name="newsletter_create"),
    path("newsletter/<int:pk>/edit/", NewsletterUpdateView.as_view(), name="newsletter_update"),
    path("newsletter/<int:pk>/delete/", NewsletterDeleteView.as_view(), name="newsletter_delete"),
    # path('newsletter/<int:pk>/send/', send_newsletter_view, name='newsletter_send'),
]
