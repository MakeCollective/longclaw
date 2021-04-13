from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView

from .forms import (
    CreateAccountForm, LoginForm
)

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



class SignupView(FormView):
    template_name = 'account/signup.html'
    form_class = CreateAccountForm
    success_url = '/account'


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


