from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

def home(request):
    return redirect('balance_list' if request.user.is_authenticated else 'login')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('promyvki/', include('promyvki.urls')),
    path('balance/', include('balance.urls')),
    path('reports/', include('reports.urls')),
]
