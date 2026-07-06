from django.contrib import admin

from .models import AntifreezeBalance, CleaningFluidBalance


admin.site.register(CleaningFluidBalance)
admin.site.register(AntifreezeBalance)