from django.urls import path
from django.conf.urls import url, include

from longclaw.subscriptions import views
from longclaw.subscriptions import api
from longclaw.settings import API_URL_PREFIX

PREFIX = 'account/subscriptions/'
API_PREFIX = API_URL_PREFIX + 'subscriptions/'

urls_no_prefix = [
    path('', views.SubscriptionIndexView.as_view(), name='subscriptions_index'),
    path('<int:subscription_id>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('create/', views.SubscriptionCreateView.as_view(), name='subscription_create'),
    path('create/success/', views.SubscriptionCreateSuccessView.as_view(), name='subscription_create_success'),
    path('test-add-to-basket/', views.test_add_to_basket, name='test_add_to_basket'),
    # path('create/confirm/', views.SubscriptionCreateConfirmView.as_view(), name='subscription_create_confirm'),
]

api_urls_no_prefix = [
    path('<int:subscription_id>/activate/', api.subscription_activate, name='subscription_activate'),
    path('<int:subscription_id>/pause/', api.subscription_pause, name='subscription_pause'),
    path('<int:subscription_id>/delete/', api.subscription_delete, name='subscription_delete'),
]

urlpatterns = [
    path(PREFIX, include(urls_no_prefix)),
    path(API_PREFIX, include(api_urls_no_prefix)),
]