from django.db import models


class CompressorStation(models.Model):
    name = models.CharField("Название КС", max_length=100, unique=True)

    def __str__(self):
        return self.name


class CleaningFluid(models.Model):
    name = models.CharField("Промывочная жидкость", max_length=100, unique=True)

    def __str__(self):
        return self.name


class Antifreeze(models.Model):
    name = models.CharField("Антифриз", max_length=100, unique=True)

    def __str__(self):
        return self.name


class Wash(models.Model):
    station = models.ForeignKey(
        CompressorStation,
        on_delete=models.CASCADE,
        verbose_name="Компрессорная станция"
    )

    date = models.DateField("Дата промывки")

    kts_before = models.DecimalField(
        "КТС до промывки",
        max_digits=8,
        decimal_places=2
    )

    kts_after = models.DecimalField(
        "КТС после промывки",
        max_digits=8,
        decimal_places=2
    )

    cleaning_fluid = models.ForeignKey(
        CleaningFluid,
        on_delete=models.PROTECT
    )

    cleaning_fluid_amount = models.DecimalField(
        "Расход жидкости (л)",
        max_digits=10,
        decimal_places=2
    )

    antifreeze = models.ForeignKey(
        Antifreeze,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    antifreeze_amount = models.DecimalField(
        "Расход антифриза (л)",
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.station} {self.date}"