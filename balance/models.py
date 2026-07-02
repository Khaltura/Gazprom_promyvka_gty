from django.db import models
from promyvki.models import (
    CompressorStation,
    CleaningFluid,
    Antifreeze
)


class CleaningFluidBalance(models.Model):
    station = models.ForeignKey(CompressorStation, on_delete=models.CASCADE)
    fluid = models.ForeignKey(CleaningFluid, on_delete=models.CASCADE)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ("station", "fluid")


class AntifreezeBalance(models.Model):
    station = models.ForeignKey(CompressorStation, on_delete=models.CASCADE)
    antifreeze = models.ForeignKey(Antifreeze, on_delete=models.CASCADE)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ("station", "antifreeze")