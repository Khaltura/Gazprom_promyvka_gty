from django.db import migrations, models


def copy_station_to_stations(apps, schema_editor):
    UserProfile = apps.get_model("users", "UserProfile")
    for profile in UserProfile.objects.exclude(station_id=None):
        profile.stations.add(profile.station_id)


class Migration(migrations.Migration):
    dependencies = [
        ("promyvki", "0003_alter_antifreeze_options_alter_cleaningfluid_options_and_more"),
        ("users", "0003_alter_userprofile_options_alter_userprofile_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="stations",
            field=models.ManyToManyField(
                blank=True,
                related_name="user_profiles",
                to="promyvki.compressorstation",
                verbose_name="Компрессорные станции",
            ),
        ),
        migrations.RunPython(copy_station_to_stations, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="userprofile",
            name="station",
        ),
    ]
