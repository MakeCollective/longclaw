from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, View

from longclaw.account.models import Account, StripePaymentMethod
from longclaw.account.forms import (
    AccountForm, SignupForm, LoginForm,
    StripePaymentMethodForm,
)
from longclaw.shipping.forms import AddressForm
from longclaw.account.utils import create_stripe_payment_method

import json
import stripe

UserModel = get_user_model()


def remove_all_users(request):
    ''' Delete all existing all users except my one, only for testing '''
    users = UserModel.objects.exclude(is_superuser=True)
    users.delete()
    return JsonResponse({'success': True})

# Views that can be used from Django and overwritten for slight modifications
# LoginView
# LogoutView
# PasswordChangeView
# PasswordChangeDoneView
# PasswordResetView
# PasswordResetDoneView
# PasswordResetConfirmView
# PasswordResetCompleteView


class LandingView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/landing.html'

    def get(self, request):
        context = {}
        return render(request, self.template_name, context=context)



class SignupView(View):
    template_name = 'longclaw/account/signup.html'
    success_url = reverse_lazy('account_landing')
    signup_form = SignupForm
    address_form = AddressForm

    def get_context_data(self, request):
        context = {
            'user_form': self.signup_form(prefix='user_form'),
            'shipping_address_form': self.address_form(prefix='shipping_address'),
            'billing_address_form': self.address_form(prefix='billing_address', use_required_attribute=False),
            'shipping_billing_address_same': True,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return context

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context=context)
    
    def post(self, request):

        # validate forms
        user_form = self.signup_form(request.POST, prefix='user_form')
        shipping_address_form = self.address_form(request.POST, prefix='shipping_address')

        shipping_billing_address_same = request.POST.get('shipping_billing_address_same')
        if not shipping_billing_address_same:
            billing_address_form = self.address_form(request.POST, prefix='billing_address', use_required_attribute=False)
        else:
            billing_address_form = self.address_form(prefix='billing_address', use_required_attribute=False)


        errors = False
        
        if not user_form.is_valid():
            errors = True
        
        if not shipping_address_form.is_valid():
            errors = True

        if not shipping_billing_address_same and not billing_address_form.is_valid():
            errors = True

        if not errors:
            account = user_form.save()
            shipping_address = shipping_address_form.save()
            account.shipping_address = shipping_address
            if not shipping_billing_address_same:
                billing_address = billing_address_form.save()
                account.billing_address = billing_address
                account.shipping_billing_address_same = False
            
            # Save the shipping/billing address(es) to the Account
            account.save()

            # Login user
            login(request, account.user)
            
            return redirect(self.success_url)
        
        context = {
            'user_form': user_form,
            'shipping_address_form': shipping_address_form,
            'billing_address_form': billing_address_form,
            'shipping_billing_address_same': shipping_billing_address_same
        }
        
        return render(request, self.template_name, context=context)


class DetailsView(LoginRequiredMixin, View):
    '''
    View for a User to see their own general details
    '''
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/details.html'

    def get(self, request):
        context = {
            'account_details_edit_url': reverse('account_details_edit'),
            'change_password_url': reverse('password_change'),
        }

        return render(request, self.template_name, context=context)


class DetailsEditView(LoginRequiredMixin, View):
    '''
    View for a User to change and save their general Account details
    '''
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/details_edit.html'
    success_url = reverse_lazy('account_details')

    def get_context_data(self, request):
        context = {}

        account = request.user.account
        account_dict = self.get_account_dict(account)
        shipping_address_dict = self.get_shipping_address_dict(account)
        billing_address_dict = self.get_billing_address_dict(account)

        context.update({
            'account_form': AccountForm(prefix='account_form', initial=account_dict),
            'shipping_address_form': AddressForm(prefix='shipping_address', initial=shipping_address_dict),
            'billing_address_form': AddressForm(prefix='billing_address', initial=billing_address_dict, use_required_attribute=False),
            'shipping_billing_address_same': account.shipping_billing_address_same,
            'account_details_url': reverse('account_details'),
        })
        return context

    def get(self, request):
        context = self.get_context_data(request)

        return render(request, self.template_name, context=context)


    def post(self, request):
        account = request.user.account
        account_form = AccountForm(request.POST, prefix='account_form', initial=self.get_account_dict(account))
        shipping_address_form = AddressForm(request.POST, prefix='shipping_address', instance=account.shipping_address)
        
        shipping_billing_address_same = request.POST.get('shipping_billing_address_same')
        if not shipping_billing_address_same:
            billing_address_form = AddressForm(request.POST, prefix='billing_address', instance=account.billing_address, use_required_attribute=False)
        else:
            # billing_address_form = AddressForm(prefix='billing_address', instance=account.billing_address, use_required_attribute=False)
            billing_address_form = None


        errors = False

        if not account_form.is_valid():
            errors = True
        
        if not shipping_address_form.is_valid():
            errors = True

        if not shipping_billing_address_same and not billing_address_form.is_valid():
            errors = True

        if not errors:

            # Check if anything changed before bothering to try and save
            if account_form.has_changed():
                account = account_form.update(account)
            
            if shipping_address_form.has_changed():
                shipping_address = shipping_address_form.save()
                account.shipping_address = shipping_address
            
            if not billing_address_form:
                account.billing_address = None
            elif billing_address_form.has_changed():
                billing_address = billing_address_form.save()
                account.billing_address = billing_address
            
            account.shipping_billing_address_same = True if shipping_billing_address_same else False
            account.save()
            
            return redirect(self.success_url)
        
        context = {
            'account_form': account_form,
            'shipping_address_form': shipping_address_form,
            'billing_address_form': billing_address_form,
            'shipping_billing_address_same': shipping_billing_address_same
        }
        
        return render(request, self.template_name, context=context)


    def get_account_dict(self, account):
        if not account:
            return {}
        account_dict = {
            'first_name': account.user.first_name,
            'last_name': account.user.last_name,
            'phone': account.phone,
            'company_name': account.company_name,
        }
        return account_dict
    
    def get_shipping_address_dict(self, account):
        if not account or not account.shipping_address:
            return {}
        shipping_address_dict = {
            'name': account.shipping_address.name,
            'line_1': account.shipping_address.line_1,
            'line_2': account.shipping_address.line_2,
            'city': account.shipping_address.city,
            'postcode': account.shipping_address.postcode,
            'country': account.shipping_address.country,
        }
        return shipping_address_dict
    
    def get_billing_address_dict(self, account):
        if not account or not account.billing_address:
            return {}
        billing_address_dict = {
            'name': account.billing_address.name,
            'line_1': account.billing_address.line_1,
            'line_2': account.billing_address.line_2,
            'city': account.billing_address.city,
            'postcode': account.billing_address.postcode,
            'country': account.billing_address.country,
        }
        return billing_address_dict


class LoginView(auth_views.LoginView):
    template_name = 'longclaw/account/login.html'
    form_class = LoginForm

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or reverse('account_landing')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_reset_url'] = reverse('password_reset')
        return context


class LogoutView(auth_views.LogoutView):
    template_name = 'longclaw/account/logout.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'longclaw/account/password/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_details_url'] = reverse('account_details')
        return context


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'longclaw/account/password/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'longclaw/account/password/password_reset.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'longclaw/account/password/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'longclaw/account/password/password_reset_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'longclaw/account/password/password_reset_complete.html'




   
class PaymentMethodIndexView(LoginRequiredMixin, TemplateView):
    ''' Index view for all existing Payment Methods ("cards") for the current account '''
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/payment_methods_index.html'

    def get_context_data(self, request):
        active_payment_method = request.user.account.stripe_active_payment_method
        if active_payment_method:
            payment_methods = StripePaymentMethod.objects.filter(account=request.user.account).exclude(id=active_payment_method.id)
        else:
            payment_methods = StripePaymentMethod.objects.filter(account=request.user.account)

        context = {
            'active_payment_method': active_payment_method,
            'payment_methods': payment_methods,
        }
        return context

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context=context)


class PaymentMethodView(LoginRequiredMixin, TemplateView):
    ''' '''
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/payment_method.html'

    def get_context_data(self, request):
        payment_method = StripePaymentMethod.objects.filter(id=self.kwargs['pm_id']).first()
        context = {
            'payment_method': payment_method,
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)

        if not context['payment_method']:
            return redirect(reverse('payment_methods_index'))

        return render(request, self.template_name, context=context)


class PaymentMethodCreateView(LoginRequiredMixin, TemplateView):
    ''' Contains the form to create a new Payment Method for the current account '''
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/payment_method_create.html'

    def get_context_data(self, request):
        stripe_payment_method_form = StripePaymentMethodForm(request.POST)
        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'stripe_payment_method_form': stripe_payment_method_form,
        }
        return context

    def get(self, request):
        context = self.get_context_data(request)

        context['stripe_payment_method_form'] = StripePaymentMethodForm(initial={
            'number': '4242424242424242',
            'expiry_month': 5,
            'expiry_year': 27,
            'cvc': 123,
        })
        
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        context = self.get_context_data(request)

        account = request.user.account

        stripe_payment_method_form = StripePaymentMethodForm(request.POST)
        if stripe_payment_method_form.is_valid():
            payment_method = stripe_payment_method_form.save(commit=False)
            payment_method.account = account
            payment_method.save()

            # If no payment method is default for an account yet, make this one the default
            if not account.active_payment_method:
                account.active_payment_method = payment_method
                
            return redirect(reverse('payment_method_create_success'))
        else:
            print('@'*80)
            print('Payment method form was not valid')
            print(stripe_payment_method_form.errors)
            print('@'*80)
        
        return render(request, self.template_name, context=context)


class PaymentMethodCreateSuccessView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'longclaw/account/payment_method_create_success.html'

    def get(self, request):
        return render(request, self.template_name, context={})


def add_payment_method_to_stripe_user(account, pm):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    print('*'*80)
    print(account)
    print(account.stripe_customer_id)
    print(pm.stripe_id)
    print('*'*80)

    response = stripe.PaymentMethod.attach(
        pm.stripe_id,
        customer=account.stripe_customer_id,
    )

    return response


def create_stripe_customer(account):
    ''' 
    Send a request to Stripe to create a Customer
    '''    
    data = {
        'address': None,
        'description': None,
        'email': account.email,
        'metadata': None,
        'name': account.user.get_full_name(),
        'payment_method': None, # Attach it after
        'phone': account.phone,
        'shipping': None,
    }
    
    if account.billing_address:
        data['address'] = {
            'city': account.billing_address.city,
            'country': 'NZ',
            'line1': account.billing_address.line_1,
            'line2': account.billing_address.line_2,
            'postal_code': account.billing_address.postcode,
        }
    
    if account.shipping_address:
        data['shipping'] = {
            'address': {
                'city': account.shipping_address.city,
                'country': 'NZ',
                'line1': account.shipping_address.line_1,
                'line2': account.shipping_address.line_2,
                'postal_code': account.shipping_address.postcode,
            },
            'name': account.user.get_full_name(),
            'phone': account.phone,
        }
    
    stripe.api_key = settings.STRIPE_SECRET_KEY

    customer = stripe.Customer.create(
        address=data['address'],
        description=data['description'],
        email=data['email'],
        metadata=data['metadata'],
        name=data['name'],
        phone=data['phone'],
        shipping=data['shipping'],
    )
    return customer




def test_stripe():
    stripe.api_key = settings.STRIPE_SECRET_KEY

    a = stripe.PaymentMethod.create(
        type='card',
        card={
            'number': '4242424242424242',
            'exp_month': 4,
            'exp_year': 2020,
            'cvc': '409',
        }
    )

    b = Account.objects.first()

    c = stripe.PaymentMethod.attach(
        a.id,
        customer=b.stripe_customer_id,
    )

    # print(a)
    print(c)

# test_stripe()