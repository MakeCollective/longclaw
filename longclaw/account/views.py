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


@login_required(login_url='/account/login/')
def LandingView(request):
    return render(request, 'account/landing.html', context={})



class SignupView(View):
    template_name = 'account/signup.html'
    # success_url = '/account'
    success_url = reverse_lazy('account_landing')

    # def get_context(self, request):
    #     context = {
    #         'user_form': SignupForm(prefix='user_form'),
    #         'shipping_address_form': AddressForm(prefix='shipping_address'),
    #         'billing_address_form': AddressForm(prefix='billing_address', use_required_attribute=False),
    #     }
    #     return context

    def get(self, request):
        context = {
            'user_form': SignupForm(prefix='user_form'),
            'shipping_address_form': AddressForm(prefix='shipping_address'),
            'billing_address_form': AddressForm(prefix='billing_address', use_required_attribute=False),
            'shipping_billing_address_same': True,
        }

        context['user_form'].fields['first_name'].widget.attrs['value'] = 'Blake'
        context['user_form'].fields['last_name'].widget.attrs['value'] = 'Gilmore'
        context['user_form'].fields['company_name'].widget.attrs['value'] = 'Blake\'s Fancy Company'
        context['user_form'].fields['email'].widget.attrs['value'] = 'pearlywite@hotmail.com'
        context['user_form'].fields['phone'].widget.attrs['value'] = '0275899010'
        context['user_form'].fields['password'].widget.attrs['value'] = 'testpassword'
        context['user_form'].fields['password_confirmation'].widget.attrs['value'] = 'testpassword'
        
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
            print('@'*80)
            print(f'No errors, so redirect to "{self.success_url}')
            print('@'*80)
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
    template_name = 'account/details.html'

    def get(self, request):
        context = {
            'account_details_edit_url': reverse('account_details_edit'),
        }

        return render(request, self.template_name, context=context)


class DetailsEditView(LoginRequiredMixin, View):
    '''
    View for a User to change and save their general Account details
    '''
    login_url = reverse_lazy('account_login')
    template_name = 'account/details_edit.html'
    success_url = reverse_lazy('account_details')

    def get(self, request):
        context = {}
        
        return render(request, self.template_name, context=context)

    def post(self, request):
        pass



class LoginView(auth_views.LoginView):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or reverse('account_landing')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_reset_url'] = reverse('password_reset')
        return context


class LogoutView(auth_views.LogoutView):
    template_name = 'account/logout.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'account/password/password_change.html'


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'account/password/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password/password_reset.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password/password_reset_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password/password_reset_complete.html'


