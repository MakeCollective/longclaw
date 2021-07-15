from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, View

from longclaw.account.forms import (
    AccountForm, SignupForm, LoginForm
)
from longclaw.shipping.forms import AddressForm

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

    def get(self, request):
        context = {
            'user_form': SignupForm(prefix='user_form'),
            'shipping_address_form': AddressForm(prefix='shipping_address'),
            'billing_address_form': AddressForm(prefix='billing_address', use_required_attribute=False),
            'shipping_billing_address_same': True,
        }
        return render(request, self.template_name, context=context)
    
    def post(self, request):

        # validate forms
        user_form = SignupForm(request.POST, prefix='user_form')
        shipping_address_form = AddressForm(request.POST, prefix='shipping_address')

        shipping_billing_address_same = request.POST.get('shipping_billing_address_same')
        if not shipping_billing_address_same:
            billing_address_form = AddressForm(request.POST, prefix='billing_address', use_required_attribute=False)
        else:
            billing_address_form = AddressForm(prefix='billing_address', use_required_attribute=False)


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

    def get(self, request):
        account = request.user.account
        account_dict = self.get_account_dict(account)
        shipping_address_dict = self.get_shipping_address_dict(account)
        billing_address_dict = self.get_billing_address_dict(account)

        context = {
            'account_form': AccountForm(prefix='account_form', initial=account_dict),
            'shipping_address_form': AddressForm(prefix='shipping_address', initial=shipping_address_dict),
            'billing_address_form': AddressForm(prefix='billing_address', initial=billing_address_dict, use_required_attribute=False),
            'shipping_billing_address_same': account.shipping_billing_address_same,
            'account_details_url': reverse('account_details'),
        }

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


