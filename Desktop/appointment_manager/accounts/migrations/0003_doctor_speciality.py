# Generated by Django 4.1.5 on 2023-09-01 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_patient_doctor'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='speciality',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]