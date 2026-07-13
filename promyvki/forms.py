from django import forms

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

        labels = {
            "station": "Компрессорная станция",
            "date": "Дата промывки",
            "kts_before": "КТС до промывки",
            "kts_after": "КТС после промывки",
            "cleaning_fluid": "Промывочная жидкость",
            "cleaning_fluid_amount": "Расход промывочной жидкости",
            "antifreeze": "Антифриз",
            "antifreeze_amount": "Расход антифриза",
        }

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "kts_before": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "kts_after": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "cleaning_fluid_amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01",
                }
            ),

            "antifreeze_amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        antifreeze = cleaned_data.get("antifreeze")
        antifreeze_amount = cleaned_data.get("antifreeze_amount")

        if antifreeze is None and antifreeze_amount:
            self.add_error(
                "antifreeze",
                "Выберите вид антифриза.",
            )

        if antifreeze is not None and not antifreeze_amount:
            self.add_error(
                "antifreeze_amount",
                "Укажите расход антифриза.",
            )

        return cleaned_data