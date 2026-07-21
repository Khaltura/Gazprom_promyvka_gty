from django.urls import path

from . import views

urlpatterns = [
    path("", views.balance_list, name="balance_list"),
    path("operations/", views.operation_list, name="operation_list"),
    path("operation/add/", views.operation_create, name="operation_create"),
    path("operation/<int:pk>/edit/", views.operation_update, name="operation_update"),
]
