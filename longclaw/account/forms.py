from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.utils.translation import gettext, gettext_lazy as _

from longclaw.account.models import Account, StripePaymentMethod
from longclaw.shipping.forms import AddressForm
from longclaw.account.utils import create_stripe_customer, create_stripe_payment_method

import stripe

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
            msg = 'Account with that email already exists'
            self.add_error('email', msg)
        
        try:
            password_validation.validate_password(password)
        except ValidationError as errors:
            for error in errors:
                self.add_error('password', error)
        
        cleaned_data['email'] = cleaned_data['email'].lower()
        
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
        
        # Create a Stripe user to save PaymentMethods against later on
        try:
            stripe_customer = create_stripe_customer(
                cleaned_data.get('email'), 
                cleaned_data.get('name'), 
                cleaned_data.get('phone'),
            )
        except Exception as e:
            raise e

        account = Account.objects.create(
            user=user,
            phone=cleaned_data.get('phone'),
            company_name=cleaned_data.get('company_name'),
            stripe_customer_id=stripe_customer.id,
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
        self.fields['username'].label = 'Email'

    def clean(self, *args, **kwargs):

        cleaned_data = super().clean(*args, **kwargs)
        cleaned_data['username'] = cleaned_data['username'].lower()
        
        return cleaned_data


class PaymentMethodForm(forms.Form):
    label = forms.CharField(label='Label')
    number = forms.CharField(label='Card number', max_length=16,
        widget=forms.TextInput(attrs={'placeholder': 'Card number'}))
    expiry_month = forms.CharField(label='Expiry month', max_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'MM'}))
    expiry_year = forms.CharField(label='Expiry year', max_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'YY'}))
    cvc = forms.CharField(label='CVC', max_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'CVC'}))


class StripePaymentMethodForm(PaymentMethodForm):
    
    name = forms.CharField(label='Name',
        widget=forms.TextInput(attrs={'placeholder': 'Name on card'}))

    field_order = ['name', 'number', 'expiry_month', 'expiry_year', 'cvc']

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Try to create the stripe StripePaymentMethod here
        try:
            pm = create_stripe_payment_method(
                cleaned_data.get('name'),
                cleaned_data.get('number'),
                cleaned_data.get('expiry_month'),
                cleaned_data.get('expiry_year'),
                cleaned_data.get('cvc')
            )
        except stripe.error.CardError as e:
            self.add_error(field=None, error=e)
        except Exception as e:
            print('!'*80)
            print('Some other exception while saving PaymentMethod:', e)
            print('!'*80)
        else:
            # Create the longclaw StripePaymentMethod and attach to account
            card = pm.get('card')
            payment_method = StripePaymentMethod(
                label=self.cleaned_data.get('label'),
                name=self.pm.get('name'),
                stripe_id=pm.get('id'),
                last4=card.get('last4'),
                payment_type=pm.get('type'),
                exp_month=card.get('exp_month'),
                exp_year=card.get('exp_year'),
            )
            return payment_method
