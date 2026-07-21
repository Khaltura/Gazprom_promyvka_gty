from django.contrib import admin
from .models import MaterialOperation

@admin.register(MaterialOperation)
class MaterialOperationAdmin(admin.ModelAdmin):
    list_display=('date','operation_type','material_type','material_name','from_station','to_station','amount','created_by')
    list_filter=('operation_type','material_type','from_station','to_station')
    search_fields=('from_station__name','to_station__name','cleaning_fluid__name','antifreeze__name','comment')
