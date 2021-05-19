from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.utils.translation import gettext, gettext_lazy as _

from longclaw.account.models import Account
from longclaw.shipping.forms import AddressForm

UserModel = get_user_model()


class RecaptchaForm(forms.Form):
    '''
    An optional addition to regular forms. Very highly suggested to use, in addition
    to the front end script to avoid a ton of spam form submissions
    '''
    recaptcha = forms.CharField(
        label='Recatpcha',
        widget=forms.HiddenInput(attrs={'data-recaptchapublickey': settings.RECAPTCHA_PUBLIC_KEY}))
    
    def clean(self, *args, **kwargs):
        # if not verify_recaptcha(self.cleaned_data.get('recaptcha')):
        #     self.add_error('__all__', 'reCAPTCHA token is invalid, please reload the page and try again')
        return super().clean(*args, **kwargs)


class AccountForm(forms.Form):
    '''
    A base form with the Account class specific fields
    '''
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    phone = forms.CharField(label='Phone')
    company_name = forms.CharField(label='Company name', required=False)

    def update(self, instance):
        # Update and save User model
        instance.user.first_name = self.cleaned_data['first_name']
        instance.user.last_name = self.cleaned_data['last_name']
        instance.user.save(update_fields=['first_name', 'last_name'])
        
        # Update and save Account model
        instance.phone = self.cleaned_data['phone']
        instance.company_name = self.cleaned_data['company_name']
        instance.save(update_fields=['phone', 'company_name'])
        
        return instance



class SignupForm(AccountForm):
    '''
    Creates an Account instance given the details entered
    '''
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password_confirmation = forms.CharField(
        label='Password confirmation', 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    # recaptcha

    field_order = ['first_name', 'last_name', 'company_name', 'email', 'phone', 'password', 'password_confirmation']
    
    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if not password:
            msg = 'Password is required'
            self.add_error('password', msg)

        if not password_confirmation:
            msg = 'Password must be provided and confirmed'
            self.add_error('password_confirmation', msg)
        
        # check if passwords match
        if password != password_confirmation:
            msg = 'Passwords did not match'
            self.add_error('password', msg)
        
        # check if user exists
        if UserModel.objects.filter(email__iexact=email).count():
            msg = 'Accout with that email already exists'
            self.add_error('email', msg)
        
        try:
            password_validation.validate_password(password)
        except ValidationError as errors:
            for error in errors:
                self.add_error('password', error)
        
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data

        if settings.ACCOUNT_REQUIRES_EMAIL_VERIFICATION:
            user = UserModel.objects.create_user(
                username=cleaned_data.get('email'),
                email=cleaned_data.get('email'),
                password=cleaned_data.get('password'),
                first_name=cleaned_data.get('first_name'),
                last_name=cleaned_data.get('last_name'),
                is_active=False, # Set to "True" when User's email is verified
            )
        else:
            user = UserModel.objects.create_user(
                username=cleaned_data.get('email'),
                email=cleaned_data.get('email'),
                password=cleaned_data.get('password'),
                first_name=cleaned_data.get('first_name'),
                last_name=cleaned_data.get('last_name'),
            )

        account = Account.objects.create(
            user=user,
            phone=cleaned_data.get('phone'),
            company_name=cleaned_data.get('company_name'),
        )
        return account        


class LoginForm(AuthenticationForm):

    error_messages = {
        'invalid_login': _(
            "Please enter a correct username/email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or email address'

    def clean(self, *args, **kwargs):
        
        return super().clean(*args, **kwargs)

