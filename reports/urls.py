from django.urls import path

from . import views

urlpatterns = [
    path("analytics/", views.analytics, name="analytics"),
    path("analytics/balance/", views.balance_analytics, name="balance_analytics"),
    path("analytics/washes/", views.wash_analytics, name="wash_analytics"),
    path("excel/", views.export_excel, name="export_excel"),
    path("excel/balance/", views.export_balance_excel, name="export_balance_excel"),
    path("excel/washes/", views.export_washes_excel, name="export_washes_excel"),
]
