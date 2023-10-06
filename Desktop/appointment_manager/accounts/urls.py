from django.contrib import admin
from django.urls import path
from .views import *
from accounts.middlewares import PermissionMiddleware

urlpatterns = [
    path('signup/',signup,name='signup'),
    path('',login_user,name='login'),
    path('user-home/',home_user,name='user_home'),
    path('admin-home/',home_admin,name='admin_home'),
    path('doctors/details/pdf/',pdf_details,name='print_doctors_details'),
    path('doctors/details/csv/',csv_details,name='csv_doctors_details'),
    path('edit-user/<int:id>/',EditUser,name='edit_user'),
    path('change-password/<int:id>/',ChangePassword,name='change_password'),
    path('group-permissions/<int:id>',GroupPermissions.as_view(),name='permissions'),
    path('group-permissions/update/<int:id>',UpdatePermissions.as_view(),name='permissions_update'),
    path('view-user/<int:id>/',ViewUser,name='view_user'),
    path('pdf-user/',render_to_pdf,name='pdf_user'),
    path('csv-user/',render_to_csv,name='csv_user'),
    path('logout/',logout_user,name='logout'),
    path('user-list/',UserList,name='user_list'),
    path('user-search/',Search,name='user_search'),
    path('validate-email',ValidateEmail,name='validate_email'),
    path('validate-mobile',ValidateMobile,name='validate_mobile'),
    path('validate-username',ValidateUsername,name='validate_username'),
    path('validate-password',ValidatePassword,name='validate_password'),
]
