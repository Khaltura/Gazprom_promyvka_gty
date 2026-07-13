from django.urls import path

from . import views


urlpatterns = [
    path("", views.wash_list, name="wash_list"),
    path("add/", views.wash_create, name="wash_create"),
]