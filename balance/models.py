from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class MaterialOperation(models.Model):
    ARRIVAL = 'arrival'
    WRITEOFF = 'writeoff'
    TRANSFER = 'transfer'
    OPERATION_TYPES = [(ARRIVAL, 'Приход'), (WRITEOFF, 'Списание'), (TRANSFER, 'Перераспределение')]

    CLEANING = 'cleaning_fluid'
    ANTIFREEZE = 'antifreeze'
    MATERIAL_TYPES = [(CLEANING, 'Промывочная жидкость'), (ANTIFREEZE, 'Антифриз')]

    operation_type = models.CharField('Тип операции', max_length=20, choices=OPERATION_TYPES)
    material_type = models.CharField('Тип материала', max_length=30, choices=MATERIAL_TYPES, default=CLEANING)
    from_station = models.ForeignKey('promyvki.CompressorStation', on_delete=models.CASCADE, null=True, blank=True, related_name='operations_from', verbose_name='Откуда')
    to_station = models.ForeignKey('promyvki.CompressorStation', on_delete=models.CASCADE, null=True, blank=True, related_name='operations_to', verbose_name='Куда')
    cleaning_fluid = models.ForeignKey('promyvki.CleaningFluid', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Промывочная жидкость')
    antifreeze = models.ForeignKey('promyvki.Antifreeze', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Антифриз')
    amount = models.DecimalField('Количество (л)', max_digits=12, decimal_places=2)
    date = models.DateField('Дата')
    comment = models.CharField('Комментарий', max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_operations', verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Операция с материалом'
        verbose_name_plural = 'Операции с материалами'
        ordering = ['-date', '-id']

    @property
    def material(self):
        return self.cleaning_fluid if self.material_type == self.CLEANING else self.antifreeze

    @property
    def material_name(self):
        return str(self.material) if self.material else '—'

    def get_available_balance(self):
        station_id = self.from_station_id
        if not station_id or not self.material:
            return Decimal('0.00')
        return calculate_material_balance(station_id, self.material_type, self.cleaning_fluid_id or self.antifreeze_id, exclude_operation_id=self.pk)

    def clean(self):
        errors = {}
        if self.amount is not None and self.amount <= 0:
            errors['amount'] = 'Количество должно быть больше нуля.'
        if self.date and self.date > timezone.localdate():
            errors['date'] = 'Дата операции не может быть в будущем.'

        if self.material_type == self.CLEANING:
            if not self.cleaning_fluid_id:
                errors['cleaning_fluid'] = 'Выберите промывочную жидкость.'
            if self.antifreeze_id:
                errors['antifreeze'] = 'Для этого типа материала антифриз не выбирается.'
        elif self.material_type == self.ANTIFREEZE:
            if not self.antifreeze_id:
                errors['antifreeze'] = 'Выберите антифриз.'
            if self.cleaning_fluid_id:
                errors['cleaning_fluid'] = 'Для этого типа материала промывочная жидкость не выбирается.'

        if self.operation_type == self.ARRIVAL:
            if self.from_station_id:
                errors['from_station'] = 'Для прихода КС-источник не указывается.'
            if not self.to_station_id:
                errors['to_station'] = 'Укажите КС-получателя.'
        elif self.operation_type == self.WRITEOFF:
            if not self.from_station_id:
                errors['from_station'] = 'Укажите КС.'
            if self.to_station_id:
                errors['to_station'] = 'Для списания КС-получатель не указывается.'
        elif self.operation_type == self.TRANSFER:
            if not self.from_station_id:
                errors['from_station'] = 'Укажите КС-источник.'
            if not self.to_station_id:
                errors['to_station'] = 'Укажите КС-получателя.'
            if self.from_station_id and self.from_station_id == self.to_station_id:
                errors['to_station'] = 'КС-источник и КС-получатель должны различаться.'

        if self.operation_type in (self.WRITEOFF, self.TRANSFER) and self.from_station_id and self.material and self.amount and self.amount > 0:
            available = self.get_available_balance()
            if self.amount > available:
                errors['amount'] = f'Недостаточно материала. Доступно: {available} л.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_operation_type_display()} — {self.material_name} — {self.amount} л'


def calculate_material_balance(station_id, material_type, material_id, exclude_operation_id=None):
    filters = {'material_type': material_type}
    filters['cleaning_fluid_id' if material_type == MaterialOperation.CLEANING else 'antifreeze_id'] = material_id
    operations = MaterialOperation.objects.filter(**filters)
    if exclude_operation_id:
        operations = operations.exclude(pk=exclude_operation_id)
    arrival = operations.filter(operation_type=MaterialOperation.ARRIVAL, to_station_id=station_id).aggregate(v=Sum('amount'))['v'] or Decimal('0')
    incoming = operations.filter(operation_type=MaterialOperation.TRANSFER, to_station_id=station_id).aggregate(v=Sum('amount'))['v'] or Decimal('0')
    outgoing = operations.filter(operation_type=MaterialOperation.TRANSFER, from_station_id=station_id).aggregate(v=Sum('amount'))['v'] or Decimal('0')
    writeoff = operations.filter(operation_type=MaterialOperation.WRITEOFF, from_station_id=station_id).aggregate(v=Sum('amount'))['v'] or Decimal('0')
    from promyvki.models import Wash
    if material_type == MaterialOperation.CLEANING:
        consumed = Wash.objects.filter(station_id=station_id, cleaning_fluid_id=material_id).aggregate(v=Sum('cleaning_fluid_amount'))['v'] or Decimal('0')
    else:
        consumed = Wash.objects.filter(station_id=station_id, antifreeze_id=material_id).aggregate(v=Sum('antifreeze_amount'))['v'] or Decimal('0')
    return arrival + incoming - outgoing - writeoff - consumed
