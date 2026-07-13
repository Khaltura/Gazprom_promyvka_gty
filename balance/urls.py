from django.urls import path
from . import views

urlpatterns = [
    path("", views.balance_list, name="balance_list"),
]