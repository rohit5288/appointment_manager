from django.db import models
from manager.constants import *
from accounts.models import *

class schedule(models.Model):
    doctor=models.OneToOneField(Doctor,on_delete=models.CASCADE)
    fromdate=models.DateField(null=True,blank=True)
    todate=models.DateField(null=True,blank=True)
    weekdays = models.PositiveIntegerField(choices=WEEKDAYS)
    openingtime=models.TimeField(null=True,blank=True)
    closingtime=models.TimeField(null=True,blank=True)
    breakstart=models.TimeField(null=True,blank=True)
    breakend=models.TimeField(null=True,blank=True)

    class Meta:
        db_table='doctor_schedule'

class AvailableSlots(models.Model):
    start=models.TimeField(null=True,blank=True)
    end=models.TimeField(null=True,blank=True)
    booking_date=models.DateField(null=True,blank=True)
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE)

class booking(models.Model):
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE)
    booking_date=models.DateField(null=True,blank=True)
    start=models.TimeField(null=True,blank=True)
    end=models.TimeField(null=True,blank=True)
    eventid=models.CharField(max_length=255,null=True,blank=True)
    class Meta:
        db_table='bookings'


class Student(models.Model):
    id=models.IntegerField(primary_key=True)
    first_name=models.CharField(max_length=255,null=True,blank=True)
    last_name=models.CharField(max_length=255,null=True,blank=True)
    ethinicity=models.CharField(max_length=255,null=True,blank=True)
    date_of_birth=models.CharField(max_length=255,null=True,blank=True)
    gender=models.CharField(max_length=1,null=True,blank=True)