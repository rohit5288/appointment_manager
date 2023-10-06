from django.shortcuts import render,redirect
from manager.constants import *
from manager.models import *
from django.http import JsonResponse
import datetime 
from datetime import timedelta
from django.contrib import messages
from django.db.models import Q
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from accounts.decorators import perm_req
from django.contrib.auth.decorators import permission_required

def get_slots(doctor_id,selected_date):
    s_obj=schedule.objects.filter(doctor_id=doctor_id)
    if s_obj:
        s=s_obj[0]
        start_time = s.openingtime
        end_time = s.closingtime
        slot_time = 30
        # Start date from today to next 5 day
        if s.fromdate<=selected_date<=s.todate:
            start_date = selected_date
            end_date = selected_date

        days = []
        while start_date <= end_date:
            hours = []
            time = start_time
            end = end_time
            while time <= end:
                slotstart=time
                slotend=(datetime.datetime.combine(start_date,time) + datetime.timedelta(minutes=slot_time)).time()
                if not s.breakstart<slotend<=s.breakend and slotend<=end:
                    hours.append((slotstart.strftime("%H:%M"),slotend.strftime("%H:%M")))
                time = slotend
            start_date += datetime.timedelta(days=1)
            days.append(hours)
        return days
    else:
        return None

def generate_date_range(start_date, end_date,days):
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in days and current_date>=datetime.date.today():
            if current_date>=datetime.date.today():
                date_range.append(current_date)
            
        current_date += timedelta(days=1)
    return date_range

@perm_req(['add_schedule','view_doctor'])
def DoctorSchedule(request):
    if request.method=="GET":
        key=list(WEEKDAYS._lookup.values())
        val=[]
        for item in key:
            val.append(WEEKDAYS.get_selected_values(item)[0])
        weekdays=list(zip(key,val))
        doctors=Doctor.objects.all()
        return render(request,'manager/schedule.html',{'weekdays':weekdays,'doctors':doctors})
    if request.method=="POST":
        weekdays=[int(i) for i in request.POST.getlist('weekdays')]
        days=sum(weekdays)
        if not schedule.objects.filter(doctor__user_id=request.user.id):
            schedule.objects.create(
                doctor= Doctor.objects.get(user_id=request.user.id),
                fromdate=request.POST.get('fromdate'),
                todate=request.POST.get('todate'),
                weekdays = days,
                openingtime= request.POST.get('openingtime'),
                closingtime= request.POST.get('closingtime'),
                breakstart= request.POST.get('breakstart'),
                breakend= request.POST.get('breakend'),
            )
            print("ADDED SCHEDULE!")

        return redirect('user_home')

@perm_req(['add_booking'])
def BookAppointment(request):
    if request.method=="GET":
        doctors=Doctor.objects.all()
        doc=[]
        for doctor in doctors:
            if not hasattr(doctor,'schedule'):
                doc.append(doctor.id)
        doctors=Doctor.objects.all().exclude(id__in=doc)
        return render(request,'manager/book_appointment.html',{'doctors':doctors})
    if request.method=="POST":
        booking.objects.create(
            patient=Patient.objects.get(user_id=request.user.id),
            doctor=Doctor.objects.get(id=request.POST.get('doctor')),
            booking_date=datetime.datetime.strptime(request.POST.get('booking_date'),"%Y-%m-%d").date(),
            slot=AvailableSlots.objects.get(id=request.POST.get('slot')),
        )
        AvailableSlots.objects.get(id=request.POST.get('slot')).delete()
        return redirect('user_home')


def daysajax(request):
    s=schedule.objects.get(doctor_id=request.GET.get('id'))
    days=list(WEEKDAYS.get_selected_keys(s.weekdays))
    dates=generate_date_range(s.fromdate,s.todate,days)
    data={'dates':dates}
    return JsonResponse(data)


def slotsajax(request):
    d= datetime.datetime.strptime(request.GET.get('date'),'%Y-%m-%d').date()
    print(d)
    if not AvailableSlots.objects.filter(Q(doctor_id=request.GET.get('id')) & Q(booking_date=d)) and not booking.objects.filter(Q(doctor_id=request.GET.get('id')) & Q(booking_date=d)):
        slots=get_slots(request.GET.get('id'),d)[0]
        for slot in slots:
            a,b=slot
            available_slots=AvailableSlots.objects.create(
                start=datetime.datetime.strptime(a,'%H:%M').time(),
                end=datetime.datetime.strptime(b,'%H:%M').time(),
                booking_date=d,
                doctor=Doctor.objects.get(id=request.GET.get('id'))
            )
    available_slots=list(AvailableSlots.objects.filter(Q(doctor_id=request.GET.get('id')) & Q(booking_date=d)).order_by('start'))
    slots=[]
    for slot in available_slots:
        slots.append((slot.id,(slot.start,slot.end)))
    data={'slots':slots}
    return JsonResponse(data)

def DeleteSchedule(request):
    data={'deleted':'false'}
    s=schedule.objects.get(id=request.GET.get('id'))
    if not s.doctor.booking_set.all():
        s.delete()
        data['deleted']='true'
    else:
        data['deleted']='false'
    return JsonResponse(data)

def DeleteEvent(request):
    credentials = Credentials(
        **request.session['credentials']
    )
    service = build('calendar', 'v3', credentials=credentials)
    data={'deleted':'false'}
    b=booking.objects.get(id=request.GET.get('bookingid'))
    AvailableSlots.objects.create(
        start=b.start,
        end=b.end,
        booking_date=b.booking_date,
        doctor=b.doctor,
    )
    b.delete()
    service.events().delete(calendarId='primary', eventId=request.GET.get('eventid')).execute()
    data['deleted']='true'
    return JsonResponse(data)