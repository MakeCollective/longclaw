from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        ''' This method allows only "email" to be used '''
        # try:
        #     # user = UserModel.objects.get(email=username)
        # except UserModel.DoesNotExist:
        #     return None
        # else:
        #     if user.check_password(password):
        #         return user

        ''' This method allows whatever field you determine (username or email at the moment) 
            to be used in as the "username"
        '''
        try:
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        except MultipleObjectsReturned:
            return User.objects.filter(email=usename).order_by('id').first()
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        
        return None