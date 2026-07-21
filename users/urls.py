from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('pending/', views.account_pending_view, name='account_pending'),
    path('logout/', views.logout_view, name='logout'),
]
