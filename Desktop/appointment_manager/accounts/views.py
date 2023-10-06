from django.shortcuts import render,redirect
from accounts.models import *
from manager.models import *
from manager.views import get_slots
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from django.db.models import Q
from accounts.constants import *
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.models import Group, Permission
from django.views import View
import re
import csv
from io import BytesIO
from xhtml2pdf import pisa
from .decorators import *
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.template.loader import get_template
from accounts.decorators import *
from datetime import datetime
import tzlocal

def home_user(request):
    
    if request.user.role==1:
        doctor=Doctor.objects.get(user_id=request.user.id)
        schdl=schedule.objects.filter(doctor_id=doctor.id)
        bookings=doctor.booking_set.all()
        if schdl:
            schdl=schdl[0]
            days=list(WEEKDAYS.get_selected_values(schdl.weekdays))
            return render(request,'users/home_user.html',{'schedule':schdl,'days':days,'bookings':bookings})
        else:
            return render(request,'users/home_user.html',{'schedule':schdl})
    else:
        patient=Patient.objects.get(user_id=request.user.id)
        appointment=booking.objects.filter(patient_id=patient.id)
        return render(request,'users/home_user.html',{'booking':appointment})


def home_admin(request):
    doctors=Doctor.objects.all()
    bookings=[]
    days=[]
    for doctor in doctors:
        bookings.append(booking.objects.filter(doctor=doctor))
        if hasattr(doctor,'schedule'):
            days.append(list(WEEKDAYS.get_selected_values(doctor.schedule.weekdays)))
    data=list(zip(doctors,bookings,days))
    return render(request,'users/home_admin.html',{'data':data})
    
def pdf_details(request):
    doctors=Doctor.objects.all()
    bookings=[]
    days=[]
    for doctor in doctors:
        bookings.append(booking.objects.filter(doctor=doctor))
        if hasattr(doctor,'schedule'):
            days.append(list(WEEKDAYS.get_selected_values(doctor.schedule.weekdays)))
    data=list(zip(doctors,bookings,days))
    template = get_template("users/home_admin.html")
    html = template.render(
        {
            "data": data
        }
    )
    pdf = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), pdf)
    res = HttpResponse(pdf.getvalue(), content_type="application/pdf")
    # res["Content-Disposition"] = f"attachment; filename=users.pdf"
    return res


def csv_details(request):
    doctors=Doctor.objects.all()
    bookings=[]
    days=[]
    for doctor in doctors:
        bookings.append(booking.objects.filter(doctor=doctor))
        if hasattr(doctor,'schedule'):
            days.append(list(WEEKDAYS.get_selected_values(doctor.schedule.weekdays)))
    data=list(zip(doctors,bookings,days))
    response = HttpResponse(content_type='text/csv')  
    response['Content-Disposition'] = 'attachment; filename="doctors_details.csv"'  
    writer = csv.writer(response)  
    writer.writerow(['NAME','SPECIALITY','DATE RANGE','WEEKDAYS','OPENING TIME','CLOSING TIME','BREAK START TIME','BREAK END TIME','BOOKINGS'])
    for doctor,bookings,days in data:
        writer.writerow([
            f'Dr. {doctor.user.first_name} {doctor.user.last_name}',
            doctor.speciality,
            f'{doctor.schedule.fromdate} to {doctor.schedule.todate}',
            [day for day in days],
            doctor.schedule.openingtime,
            doctor.schedule.closingtime,
            doctor.schedule.breakstart,
            doctor.schedule.breakend,
            [f'{booking.start} to {booking.end} on {booking.booking_date} by Mr. {booking.patient.user.first_name} {booking.patient.user.last_name}' for booking in bookings]
            ])
    return response
        

def login_user(request):
    if request.method=="GET":
        return render(request,'Authentication/login.html')
    if request.method=="POST":
        user_cred=request.POST.get('user')
        pwd=request.POST.get('psw')
        usr=authenticate(username=user_cred, password=pwd)
        if usr is not None:
            login(request,usr)
            if usr.is_superuser==1:
                return redirect('admin_home')
            else:
                return redirect('user_home')
        else:
            return redirect('login')
    
    

def signup(request):
    if request.method == "GET":
         return render(request,'Authentication/signup.html')
    if request.method == "POST":
        if request.POST.get('username').strip() =='' or request.POST.get('first_name').strip() =='' or request.POST.get('last_name').strip() =='' or request.POST.get('email').strip() =='' or request.POST.get('mobile_no').strip() =='' or request.POST.get('psw').strip() =='': 
            messages.add_message(request,messages.INFO,"ERROR: Do not submit empty fields")
            return render(request,'Authentication/signup.html')
        else:
            new_user=User.objects.create(username = request.POST.get('username'),
                                first_name = request.POST.get('first_name'),
                                last_name = request.POST.get('last_name'),
                                email = request.POST.get('email'),
                                mobile_no=request.POST.get('mobile_no'),
                                password = make_password(request.POST.get('psw')),
                                role=request.POST.get('role')
                                )
            if new_user.role=='1':
                Doctor.objects.create(user=new_user,speciality=request.POST.get('speciality'))
                group=Group.objects.get(name="Doctors")
                new_user.groups.add(group)

            elif new_user.role=='2':
                Patient.objects.create(user=new_user)
                group=Group.objects.get(name="Patients")
                new_user.groups.add(group)
            return redirect('login')


def logout_user(request):
    user=request.user
    logout(request)
    messages.add_message(request,messages.INFO,f"{user} logged out succesfully.")
    return render(request,'Authentication/login.html')

from django.utils import timezone
import pytz
@admin_required()
def UserList(request):
        timezone.activate(pytz.timezone(str(tzlocal.get_localzone())))
        users = User.objects.exclude(is_superuser=1).order_by('role','created')
        return render(request,"users/users-list.html",{"users":users,'groups':Group.objects.all()})


class GroupPermissions(View):
    def get(self,request,id):
        group=Group.objects.get(id=id)
        permitted=[]
        group_permissions=group.permissions.all()
        for p in group_permissions:
            permitted.append(p.id)
        permissions=Permission.objects.all().order_by('id')
        return render(request,'users/permissions.html',{'group':group,'permitted':permitted,'permissions':permissions})
    def post(self,request,id):
        group=Group.objects.get(id=id)
        for p_id in request.POST.getlist('permissions'):
            group.permissions.add(p_id)
        group.save()
        return redirect('user_list')


class UpdatePermissions(View):
    def get(self,request,id):
        group=Group.objects.get(id=id)
        permitted=[]
        group_permissions=group.permissions.all()
        for p in group_permissions:
            permitted.append(p.id)
        permissions=Permission.objects.all().order_by('id')
        return render(request,'users/permissions_update.html',{'group':group,'permitted':permitted,'permissions':permissions})
    def post(self,request,id):
        group=Group.objects.get(id=id)
        group.permissions.clear()
        for p_id in request.POST.getlist('permissions'):
            group.permissions.add(p_id)
        group.save()
        return redirect('user_list')

def Search(request):
    timezone.activate(pytz.timezone(str(tzlocal.get_localzone())))
    if request.method=="POST":
        users=User.objects.exclude(is_superuser=1).order_by('created','id')
        if request.POST.get('username'):
            users=users.filter(username__icontains=request.POST.get('username'))
        if request.POST.get('name'):                                
            users=users.filter(Q(first_name__icontains=request.POST.get('name'))|Q(last_name__icontains=request.POST.get('name')))
        if request.POST.get('email'):
            users=users.filter(email__icontains=request.POST.get('email'))
        if request.POST.get('created'):
            res=[]
            for user in users:
                user.created=user.created.astimezone(tzlocal.get_localzone())
                if (user.created.date()==datetime.strptime(request.POST.get('created'),"%Y-%m-%d").date()):
                    res.append(user)
            users=res
        return render(request,"users/users-list.html",{"users":users})
    timezone.deactivate()
    return redirect('user_list')
s="sldjf"
s.lower()
str()

def EditUser(request,id):
    if request.method == "GET":
        user=User.objects.get(id=id)
        return render(request,"users/update-user.html",{"user":user})
    if request.method == "POST":
        user=User.objects.get(id=id)
        if request.POST.get('first_name'):
            user.first_name =request.POST.get('first_name')
        if request.POST.get('last_name'):
            user.last_name =request.POST.get('last_name')
        if request.POST.get('email'):
            user.email =request.POST.get('email')
        if request.FILES.get('profile_pic'):
            user.profile_pic=request.FILES.get('profile_pic')
        user.save()
        return redirect("user_list")
    

def ChangePassword(request,id):
    if request.method == "GET":
        return render(request,"users/change_pwd.html")
    if request.method == "POST":
        user=User.objects.get(id=id)
        user.set_password(request.POST.get('new_pwd'))
        user.save()
        messages.add_message(request,messages.INFO,"Password changed successfully! Login again using your new password.")
        return redirect('login')
    

def ViewUser(request,id):
    user=User.objects.get(id=id)
    return render(request,'users/user_view.html',{'user':user})


def render_to_pdf(request):
    users = User.objects.exclude(is_superuser=1).order_by('created','id')
    template = get_template("users/users_pdf.html")
    html = template.render(
        {
            "users": users
        }
    )
    pdf = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), pdf)
    res = HttpResponse(pdf.getvalue(), content_type="application/pdf")
    return res



def render_to_csv(request):
    users = User.objects.exclude(is_superuser=1).order_by('created','id')
    response = HttpResponse(content_type='text/csv')  
    response['Content-Disposition'] = 'attachment; filename="users.csv"'  
    writer = csv.writer(response)  
    writer.writerow(['ID','USERNAME','NAME','EMAIL','CREATED ON'])
    for user in users:
        writer.writerow([user.id,user.username,user.first_name+" "+user.last_name,user.email,user.created])  
    return response


def ValidateUsername(request):
    data = {"is_exists":"false"}
    username = User.objects.filter(username = request.GET.get('username'))
    if username:
        data['is_exists']="true"
    else:
         data['is_exists']="false"
    return JsonResponse(data)


def ValidateEmail(request):
    data = {"is_exists":"false","email":'false'}
    email = User.objects.filter(email = request.GET.get('email'))
    if email:
        data['is_exists']="true"
    else:
         data['is_exists']="false"
    if re.fullmatch(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',request.GET.get('email')):
        data['email']='true'
    else:
        data['email']='false'
    return JsonResponse(data)


def ValidateMobile(request):
    data = {"is_exists":"false","number":"false"}
    mobile=User.objects.filter(mobile_no=request.GET.get('mobile'))
    if mobile:
        data["is_exists"]="true"

    else:
        data["is_exists"]="false"
    if re.fullmatch(r'[0-9]*',request.GET.get('mobile')):
        data["number"]="true"
    else:
        data["number"]="false"
    return JsonResponse(data)


def ValidatePassword(request):
    data = {"is_exists":"false"}
    user = User.objects.get(id = request.GET.get('id'))
    if user.check_password(request.GET.get('pwd')):
        data["is_exists"]="true"
    else:
        data["is_exists"]="false"
    return JsonResponse(data)

