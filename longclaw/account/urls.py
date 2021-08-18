from django.urls import path
from django.conf.urls import url, include

from longclaw.settings import API_URL_PREFIX
from longclaw.account import views
from longclaw.account import api

PREFIX = 'account/'
API_PREFIX = API_URL_PREFIX + 'account/'

urls_no_prefix = [
    path('', views.LandingView.as_view(), name='account_landing'),
    path('signup/', views.SignupView.as_view(), name='account_signup'),
    path('details/', views.DetailsView.as_view(), name='account_details'),
    path('details/edit/', views.DetailsEditView.as_view(), name='account_details_edit'),
    
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
    # path('remove_all_users/', views.remove_all_users, name='remove_all_users'),

    path('payment-methods/', views.PaymentMethodIndexView.as_view(), name='payment_methods_index'),
    path('payment-methods/<int:pm_id>/', views.PaymentMethodView.as_view(), name='payment_method'),
    path('payment-methods/create/', views.PaymentMethodCreateView.as_view(), name='payment_method_create'),
    path('payment-methods/create/success/', views.PaymentMethodCreateSuccessView.as_view(), name='payment_method_create_success'),
]

api_urls_no_prefix = [
    path('payment-methods/<int:pm_id>/set-default/', api.payment_method_set_default, name='payment_method_set_default'),
    path('payment-methods/<int:pm_id>/delete/', api.payment_method_deactivate, name='payment_method_deactivate'),

]

urlpatterns = [
    path(PREFIX, include(urls_no_prefix)),
    path(API_PREFIX, include(api_urls_no_prefix)),
]