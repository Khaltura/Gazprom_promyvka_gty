from django import forms

from users.utils import user_stations

from .models import Wash


class WashForm(forms.ModelForm):
    class Meta:
        model = Wash
        fields = (
            "station",
            "date",
            "kts_before",
            "kts_after",
            "cleaning_fluid",
            "cleaning_fluid_amount",
            "antifreeze",
            "antifreeze_amount",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "kts_before": forms.NumberInput(attrs={"step": "0.01"}),
            "kts_after": forms.NumberInput(attrs={"step": "0.01"}),
            "cleaning_fluid_amount": forms.NumberInput(attrs={"step": "0.01"}),
            "antifreeze_amount": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fixed_station = None

        if user and user.is_authenticated and not user.is_superuser:
            assigned = user_stations(user)
            self.fields["station"].queryset = assigned

            if assigned.count() == 1:
                self.fixed_station = assigned.first()
                self.fields["station"].initial = self.fixed_station
                self.fields["station"].widget = forms.HiddenInput()

    def clean(self):
        data = super().clean()
        if self.user and not self.user.is_superuser:
            assigned_ids = set(user_stations(self.user).values_list("id", flat=True))
            station = data.get("station")
            if not assigned_ids:
                raise forms.ValidationError("Администратор ещё не назначил вам КС.")

            if self.fixed_station:
                station = self.fixed_station
                data["station"] = self.fixed_station
                self.instance.station = self.fixed_station

            if not station or station.id not in assigned_ids:
                self.add_error("station", "Выберите одну из назначенных вам КС.")
        return data
