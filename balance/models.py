from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


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
        verbose_name="Откуда",
    )

    to_station = models.ForeignKey(
        "promyvki.CompressorStation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transfer_to",
        verbose_name="Куда",
    )

    cleaning_fluid = models.ForeignKey(
        "promyvki.CleaningFluid",
        on_delete=models.CASCADE,
        verbose_name="Промывочная жидкость",
    )

    amount = models.DecimalField(
        "Количество (л)",
        max_digits=10,
        decimal_places=2,
    )

    date = models.DateField("Дата")

    comment = models.CharField(
        "Комментарий",
        max_length=255,
        blank=True,
    )

    def get_available_balance(self):
        """
        Возвращает доступный остаток выбранной промывочной жидкости
        на станции-источнике.

        Используется для проверки списания и перераспределения.
        """
        if self.from_station_id is None or self.cleaning_fluid_id is None:
            return Decimal("0.00")

        operations = MaterialOperation.objects.filter(
            cleaning_fluid_id=self.cleaning_fluid_id,
        )

        arrival = (
            operations.filter(
                operation_type="arrival",
                to_station_id=self.from_station_id,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        transfer_in = (
            operations.filter(
                operation_type="transfer",
                to_station_id=self.from_station_id,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        transfer_out = (
            operations.filter(
                operation_type="transfer",
                from_station_id=self.from_station_id,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        writeoff = (
            operations.filter(
                operation_type="writeoff",
                from_station_id=self.from_station_id,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        # Импорт внутри метода позволяет избежать лишних циклических импортов.
        from promyvki.models import Wash

        wash = (
            Wash.objects.filter(
                station_id=self.from_station_id,
                cleaning_fluid_id=self.cleaning_fluid_id,
            ).aggregate(total=Sum("cleaning_fluid_amount"))["total"]
            or Decimal("0.00")
        )

        available_balance = (
            arrival
            + transfer_in
            - transfer_out
            - writeoff
            - wash
        )

        return available_balance

    def clean(self):
        errors = {}

        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "Количество должно быть больше нуля."

        if self.date and self.date > timezone.localdate():
            errors["date"] = "Дата операции не может быть в будущем."

        if self.operation_type == "arrival":
            if self.from_station is not None:
                errors["from_station"] = (
                    "Для прихода станция-источник не указывается."
                )

            if self.to_station is None:
                errors["to_station"] = (
                    "Для прихода необходимо указать КС-получателя."
                )

        elif self.operation_type == "writeoff":
            if self.from_station is None:
                errors["from_station"] = (
                    "Для списания необходимо указать КС."
                )

            if self.to_station is not None:
                errors["to_station"] = (
                    "Для списания станция-получатель не указывается."
                )

        elif self.operation_type == "transfer":
            if self.from_station is None:
                errors["from_station"] = (
                    "Для перераспределения укажите КС-источник."
                )

            if self.to_station is None:
                errors["to_station"] = (
                    "Для перераспределения укажите КС-получателя."
                )

            if (
                self.from_station is not None
                and self.to_station is not None
                and self.from_station_id == self.to_station_id
            ):
                errors["to_station"] = (
                    "Нельзя перераспределить жидкость на ту же КС."
                )

        if self.operation_type in ("writeoff", "transfer"):
            can_check_balance = (
                self.from_station_id is not None
                and self.cleaning_fluid_id is not None
                and self.amount is not None
                and self.amount > 0
            )

            if can_check_balance:
                available_balance = self.get_available_balance()

                # При редактировании уже существующей операции её старое
                # количество уже вычтено из текущего баланса.
                # Поэтому возвращаем его перед сравнением.
                if self.pk:
                    old_operation = (
                        MaterialOperation.objects
                        .filter(pk=self.pk)
                        .first()
                    )

                    if (
                        old_operation is not None
                        and old_operation.operation_type
                        in ("writeoff", "transfer")
                        and old_operation.from_station_id
                        == self.from_station_id
                        and old_operation.cleaning_fluid_id
                        == self.cleaning_fluid_id
                    ):
                        available_balance += old_operation.amount

                if self.amount > available_balance:
                    errors["amount"] = (
                        "Недостаточно жидкости на выбранной КС. "
                        f"Доступно: {available_balance} л."
                    )

        if errors:
            raise ValidationError(errors)

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"
        ordering = ["-date", "-id"]

    def __str__(self):
        return (
            f"{self.get_operation_type_display()} — "
            f"{self.cleaning_fluid} — {self.amount} л"
        )