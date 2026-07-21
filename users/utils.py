from promyvki.models import CompressorStation


def user_stations(user):
    """Возвращает КС, доступные пользователю."""
    if user.is_superuser:
        return CompressorStation.objects.all()
    profile = getattr(user, "profile", None)
    if not profile:
        return CompressorStation.objects.none()
    return profile.stations.all()


def has_assigned_stations(user):
    return user.is_superuser or user_stations(user).exists()
