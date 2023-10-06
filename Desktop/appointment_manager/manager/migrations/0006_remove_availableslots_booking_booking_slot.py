# Generated by Django 4.1.5 on 2023-09-04 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0005_alter_availableslots_doctor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availableslots',
            name='booking',
        ),
        migrations.AddField(
            model_name='booking',
            name='slot',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='manager.availableslots'),
            preserve_default=False,
        ),
    ]