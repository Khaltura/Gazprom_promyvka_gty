from django.contrib import admin
from .models import Antifreeze,CleaningFluid,CompressorStation,Wash

@admin.register(CompressorStation)
class CompressorStationAdmin(admin.ModelAdmin): search_fields=('name',)
@admin.register(CleaningFluid)
class CleaningFluidAdmin(admin.ModelAdmin): search_fields=('name',)
@admin.register(Antifreeze)
class AntifreezeAdmin(admin.ModelAdmin): search_fields=('name',)
@admin.register(Wash)
class WashAdmin(admin.ModelAdmin):
    list_display=('date','station','cleaning_fluid','cleaning_fluid_amount','antifreeze','antifreeze_amount','created_by')
    list_filter=('station','cleaning_fluid','antifreeze')
