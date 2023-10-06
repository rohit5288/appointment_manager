# Generated by Django 4.1.5 on 2023-09-04 06:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_alter_booking_doctor_alter_booking_patient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='end',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='start',
        ),
        migrations.CreateModel(
            name='AvailableSlots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField(blank=True, null=True)),
                ('end', models.TimeField(blank=True, null=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.booking')),
            ],
        ),
    ]