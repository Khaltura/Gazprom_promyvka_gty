from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('users', '0001_initial'), ('promyvki', '0001_initial')]
    operations = [
        migrations.AlterField(
            model_name='userprofile', name='station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='promyvki.compressorstation', verbose_name='Компрессорная станция'),
        ),
    ]
