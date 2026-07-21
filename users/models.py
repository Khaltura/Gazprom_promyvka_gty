from django.contrib.auth.models import User
from django.db import models

from promyvki.models import CompressorStation


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    stations = models.ManyToManyField(
        CompressorStation,
        blank=True,
        related_name="user_profiles",
        verbose_name="Компрессорные станции",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        names = ", ".join(self.stations.values_list("name", flat=True))
        return f"{self.user.username} — {names or 'КС не назначена'}"
