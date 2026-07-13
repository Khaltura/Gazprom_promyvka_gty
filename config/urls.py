from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("promyvki/", include("promyvki.urls")),
    path("balance/", include("balance.urls")),
]