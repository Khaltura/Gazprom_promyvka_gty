from django import forms

from promyvki.models import CompressorStation
from users.utils import user_stations

from .models import MaterialOperation


class MaterialOperationForm(forms.ModelForm):
    class Meta:
        model = MaterialOperation
        fields = (
            "operation_type",
            "material_type",
            "from_station",
            "to_station",
            "cleaning_fluid",
            "antifreeze",
            "amount",
            "date",
            "comment",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fixed_station = None

        if user and user.is_authenticated and not user.is_superuser:
            assigned = user_stations(user)
            self.fields["from_station"].queryset = assigned
            # Для прихода пользователь может принять материал только на одну из своих КС.
            # Для перераспределения станция назначения может быть любой.
            self.fields["to_station"].queryset = CompressorStation.objects.all()

            if assigned.count() == 1:
                self.fixed_station = assigned.first()
                self.fields["from_station"].initial = self.fixed_station
                self.fields["from_station"].widget = forms.HiddenInput()

                if not self.is_bound and not self.instance.pk:
                    self.fields["to_station"].initial = self.fixed_station

    def clean(self):
        data = super().clean()
        user = self.user
        operation_type = data.get("operation_type")
        from_station = data.get("from_station")
        to_station = data.get("to_station")

        if user and user.is_authenticated and not user.is_superuser:
            assigned_ids = set(user_stations(user).values_list("id", flat=True))
            if not assigned_ids:
                raise forms.ValidationError("Администратор ещё не назначил вам КС.")

            if self.fixed_station:
                if operation_type == MaterialOperation.ARRIVAL:
                    to_station = self.fixed_station
                    data["to_station"] = self.fixed_station
                    self.instance.to_station = self.fixed_station
                else:
                    from_station = self.fixed_station
                    data["from_station"] = self.fixed_station
                    self.instance.from_station = self.fixed_station

            if operation_type == MaterialOperation.ARRIVAL:
                if not to_station or to_station.id not in assigned_ids:
                    self.add_error("to_station", "Приход можно оформить только на назначенную вам КС.")
                data["from_station"] = None
                self.instance.from_station = None
            else:
                if not from_station or from_station.id not in assigned_ids:
                    self.add_error("from_station", "Выберите одну из назначенных вам КС.")

        if data.get("material_type") == MaterialOperation.CLEANING:
            data["antifreeze"] = None
            self.instance.antifreeze = None
        else:
            data["cleaning_fluid"] = None
            self.instance.cleaning_fluid = None

        if operation_type == MaterialOperation.ARRIVAL:
            data["from_station"] = None
            self.instance.from_station = None
        elif operation_type == MaterialOperation.WRITEOFF:
            data["to_station"] = None
            self.instance.to_station = None

        return data
