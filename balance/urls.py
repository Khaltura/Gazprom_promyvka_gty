from django.urls import path

from . import views


urlpatterns = [
    path("", views.balance_list, name="balance_list"),
    path(
        "operation/add/",
        views.operation_create,
        name="operation_create",
    ),
]