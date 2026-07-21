from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class CompressorStation(models.Model):
    name = models.CharField('Название КС', max_length=100, unique=True)
    class Meta:
        verbose_name = 'Компрессорная станция'
        verbose_name_plural = 'Компрессорные станции'
        ordering = ['name']
    def __str__(self): return self.name

class CleaningFluid(models.Model):
    name = models.CharField('Промывочная жидкость', max_length=100, unique=True)
    class Meta:
        verbose_name = 'Промывочная жидкость'
        verbose_name_plural = 'Промывочные жидкости'
        ordering = ['name']
    def __str__(self): return self.name

class Antifreeze(models.Model):
    name = models.CharField('Антифриз', max_length=100, unique=True)
    class Meta:
        verbose_name = 'Антифриз'
        verbose_name_plural = 'Антифризы'
        ordering = ['name']
    def __str__(self): return self.name

class Wash(models.Model):
    station = models.ForeignKey(CompressorStation, on_delete=models.CASCADE, verbose_name='Компрессорная станция')
    date = models.DateField('Дата промывки')
    kts_before = models.DecimalField('КТС до промывки', max_digits=8, decimal_places=2)
    kts_after = models.DecimalField('КТС после промывки', max_digits=8, decimal_places=2)
    cleaning_fluid = models.ForeignKey(CleaningFluid, on_delete=models.PROTECT, verbose_name='Промывочная жидкость')
    cleaning_fluid_amount = models.DecimalField('Расход жидкости (л)', max_digits=12, decimal_places=2)
    antifreeze = models.ForeignKey(Antifreeze, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Антифриз')
    antifreeze_amount = models.DecimalField('Расход антифриза (л)', max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='washes', verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Промывка'
        verbose_name_plural = 'Промывки'
        ordering = ['-date', '-id']

    def clean(self):
        errors = {}
        if self.date and self.date > timezone.localdate(): errors['date'] = 'Дата не может быть в будущем.'
        if self.cleaning_fluid_amount is not None and self.cleaning_fluid_amount <= 0: errors['cleaning_fluid_amount'] = 'Расход должен быть больше нуля.'
        if self.antifreeze_amount is not None and self.antifreeze_amount < 0: errors['antifreeze_amount'] = 'Расход не может быть отрицательным.'
        if not self.antifreeze_id and self.antifreeze_amount: errors['antifreeze'] = 'Выберите антифриз.'
        if self.antifreeze_id and not self.antifreeze_amount: errors['antifreeze_amount'] = 'Укажите расход антифриза.'
        if self.station_id and self.cleaning_fluid_id and self.cleaning_fluid_amount and self.cleaning_fluid_amount > 0:
            from balance.models import calculate_material_balance, MaterialOperation
            available = calculate_material_balance(self.station_id, MaterialOperation.CLEANING, self.cleaning_fluid_id)
            if self.pk:
                old = Wash.objects.filter(pk=self.pk).first()
                if old and old.station_id == self.station_id and old.cleaning_fluid_id == self.cleaning_fluid_id: available += old.cleaning_fluid_amount
            if self.cleaning_fluid_amount > available: errors['cleaning_fluid_amount'] = f'Недостаточно жидкости. Доступно: {available} л.'
        if self.station_id and self.antifreeze_id and self.antifreeze_amount and self.antifreeze_amount > 0:
            from balance.models import calculate_material_balance, MaterialOperation
            available = calculate_material_balance(self.station_id, MaterialOperation.ANTIFREEZE, self.antifreeze_id)
            if self.pk:
                old = Wash.objects.filter(pk=self.pk).first()
                if old and old.station_id == self.station_id and old.antifreeze_id == self.antifreeze_id: available += old.antifreeze_amount
            if self.antifreeze_amount > available: errors['antifreeze_amount'] = f'Недостаточно антифриза. Доступно: {available} л.'
        if errors: raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self): return f'{self.station} — {self.date}'
