from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class CustomBackend(BaseBackend):
    def authenticate(self,request,username=None,password=None):
        UserModel=get_user_model()
        try:
            user=UserModel.objects.get(Q(email__exact=username)|Q(username__exact=username))
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None