from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.utils.translation import gettext, gettext_lazy as _

UserModel = get_user_model()


class RecaptchaForm(forms.Form):
    '''
    An optioanl addition to regular forms. Very highly suggested to use, in addition
    to the front end scirpt to avoid
    a ton of spam form submissions
    '''
    recaptcha = forms.CharField(
        label='Recatpcha',
        widget=forms.HiddenInput(attrs={'data-recaptchapublickey': settings.RECAPTCHA_PUBLIC_KEY}))


class AccountForm(forms.Form):
    '''
    A base form with the Account class specific fields
    '''
    name = forms.CharField(label='Name')
    phone = forms.CharField(label='Phone')
    company_name = forms.CharField(label='Company name', required=False)


class CreateAccountForm(AccountForm):
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

    field_order = ['name', 'company_name', 'email', 'phone', 'password', 'password_confirmation']
    

class LoginForm(AuthenticationForm):

    # recaptcha = forms.CharField(
    #     label='Recaptcha',
    #     widget=forms.HiddenInput(attrs={'data-recaptchapublickey': settings.RECAPTCHA_PUBLIC_KEY, 'class': 'recaptcha-input'})
    # )

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

        # if not verify_recaptcha(self.cleaned_data.get('recaptcha')):
        #     self.add_error('__all__', 'reCAPTCHA token is invalid, please reload the page and try again')
        
        return super().clean(*args, **kwargs)

