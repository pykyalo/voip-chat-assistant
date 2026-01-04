from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_document, name="upload_document"),
    path("send/", views.send_message, name="send_message"),
    path("clear/", views.clear_chat, name="clear_chat"),
]
