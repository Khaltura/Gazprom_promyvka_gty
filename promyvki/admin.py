from django.contrib import admin

from .models import Antifreeze, CleaningFluid, CompressorStation, Wash


admin.site.register(CompressorStation)
admin.site.register(CleaningFluid)
admin.site.register(Antifreeze)
admin.site.register(Wash)