from django.contrib import admin
from django.urls import path
from .views import *
from accounts.middlewares import PermissionMiddleware

urlpatterns = [
    path('schedule/',DoctorSchedule,name='schedule'),
    path('book-appointment/',BookAppointment,name='book_appointment'),
    path('load-dates/',daysajax,name='load_dates'),
    path('load-slots/',slotsajax,name='load_slots'),
    path('delete-schedule/',DeleteSchedule,name='delete_schedule'),
    path('delete-event/',DeleteEvent,name='delete_event')
    ]