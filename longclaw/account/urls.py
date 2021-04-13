from django.urls import path
from django.conf.urls import url, include

from longclaw.account import views

PREFIX = 'account/'

urls_no_prefix = [
    path('', views.LandingView, name='account_landing'),
    path('signup/', views.SignupView.as_view(), name='account_signup'),
    # path('details/', views.DetailsView, name='account_details'), # TODO
    
    # path('delete/', views.AccountDeleteView, name='account_delete'), #TODO
    # path('delete/done/', views.AccountDeleteDoneView, name='account_delete_done'), #TODO

    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # path('email_verification/', views.AccountEmailVerificationView, name='account_email_verification'),
    # path('email_verification_confirm/', views.AccountEmailVerificationConfirmView, name='account_email_verification_confirm'),
]

urlpatterns = [
    path(PREFIX, include(urls_no_prefix))
]