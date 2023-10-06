# custom_permission_middleware.py

from django.http import HttpResponseForbidden
from django.urls import reverse
from manager.models import *  # Import your models and permissions
from django.contrib.auth.models import Group


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            if not request.user in Group.objects.get(name="Doctors").user_set.all() and request.path in ['/schedule/','/delete-schedule/']:
                return HttpResponseForbidden("<h1>ERROR: Forbidden request</h1><h3 style='color:red;'>You are not Authorised to do this Task.</h3>")
            
            if not request.user.has_perm('manager.add_booking') and request.path == '/book-appointment/':
                return HttpResponseForbidden("<h1>ERROR: Forbidden request</h1><h3 style='color:red;'>You are not Authorised to do this Task.</h3>")
            if not request.user.has_perms(['manager.add_schedule','manager.view_schedule','manager.delete_schedule']) and request.path in ['/schedule/']:
                return HttpResponseForbidden("<h1>ERROR: Forbidden request</h1><h3 style='color:red;'>You are not Authorised to do this Task.</h3>")
            
            if not request.user.is_superuser==1 and request.path == '/user-list/':
                return HttpResponseForbidden("<h1>ERROR: Forbidden request</h1><h3 style='color:red;'>You are not Authorised to do this Task.</h3>")
        return response