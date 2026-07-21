from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "station_list")
    list_filter = ("stations",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "stations__name",
    )
    filter_horizontal = ("stations",)

    @admin.display(description="Компрессорные станции")
    def station_list(self, obj):
        return ", ".join(obj.stations.values_list("name", flat=True)) or "Не назначены"
