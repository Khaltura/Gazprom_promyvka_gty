from django.db import models


class MaterialOperation(models.Model):

    OPERATION_TYPES = [
        ("arrival", "Приход"),
        ("writeoff", "Списание"),
        ("transfer", "Перераспределение"),
    ]

    operation_type = models.CharField(
        "Тип операции",
        max_length=20,
        choices=OPERATION_TYPES,
    )

    from_station = models.ForeignKey(
        "promyvki.CompressorStation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transfer_from",
        verbose_name="Откуда"
    )

    to_station = models.ForeignKey(
        "promyvki.CompressorStation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transfer_to",
        verbose_name="Куда"
    )

    cleaning_fluid = models.ForeignKey(
        "promyvki.CleaningFluid",
        on_delete=models.CASCADE,
        verbose_name="Промывочная жидкость"
    )

    amount = models.DecimalField(
        "Количество (л)",
        max_digits=10,
        decimal_places=2
    )

    date = models.DateField("Дата")

    comment = models.CharField(
        "Комментарий",
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"

    def __str__(self):
        return f"{self.get_operation_type_display()} ({self.amount} л)"