from django.contrib import admin
from .models import MaterialOperation


@admin.register(MaterialOperation)
class MaterialOperationAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "operation_type",
        "from_station",
        "to_station",
        "cleaning_fluid",
        "amount",
    )

    list_filter = (
        "operation_type",
        "from_station",
        "to_station",
        "cleaning_fluid",
    )

    search_fields = (
        "from_station__name",
        "to_station__name",
        "cleaning_fluid__name",
    )