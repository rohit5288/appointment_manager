from functools import wraps
from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponseForbidden

def admin_required():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_superuser==1:
                messages.add_message(request,messages.INFO,"ACCESS DENIED! LOGIN AS ADMIN.")
                return redirect('login')
            else:
                return view(request)   
        return _wrapped_view
    return decorator

def perm_req(perm_list):
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request,*args,**kwargs):
            for permission in perm_list:
                if not request.user.has_perm(permission):
                    return HttpResponseForbidden("<h1>ERROR: Forbidden request</h1><h3 style='color:red;'>You are not Authorised to do this Task.</h3>")
            return view(request)   
        return _wrapped_view
    return decorator