from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def set_cleaning_type(apps, schema_editor):
    Operation = apps.get_model('balance', 'MaterialOperation')
    Operation.objects.all().update(material_type='cleaning_fluid')

class Migration(migrations.Migration):
    dependencies = [('balance', '0005_alter_materialoperation_options'), ('promyvki', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='materialoperation', name='material_type', field=models.CharField(choices=[('cleaning_fluid','Промывочная жидкость'),('antifreeze','Антифриз')], default='cleaning_fluid', max_length=30, verbose_name='Тип материала')),
        migrations.AlterField(model_name='materialoperation', name='cleaning_fluid', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='promyvki.cleaningfluid', verbose_name='Промывочная жидкость')),
        migrations.AddField(model_name='materialoperation', name='antifreeze', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='promyvki.antifreeze', verbose_name='Антифриз')),
        migrations.AddField(model_name='materialoperation', name='created_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='material_operations', to=settings.AUTH_USER_MODEL, verbose_name='Создал')),
        migrations.AddField(model_name='materialoperation', name='created_at', field=models.DateTimeField(auto_now_add=True, null=True)),
        migrations.RunPython(set_cleaning_type, migrations.RunPython.noop),
    ]
