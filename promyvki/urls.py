from django.urls import path

from . import views


urlpatterns = [
    path("", views.wash_list, name="wash_list"),
]