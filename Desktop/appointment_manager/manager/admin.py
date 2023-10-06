from django.contrib import admin
from django.contrib.auth.models import User
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from impersonate.admin import UserAdminImpersonateMixin


class NewUserAdmin(UserAdminImpersonateMixin, UserAdmin):
    open_new_window = True
    pass

admin.site.register(User, NewUserAdmin)