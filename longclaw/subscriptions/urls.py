from django.urls import path
from django.conf.urls import url, include

from longclaw.subscriptions import views

PREFIX = 'account/subscriptions/'

urls_no_prefix = [
    path('', views.SubscriptionIndexView.as_view(), name='subscriptions_index'),
    path('create/', views.SubscriptionCreateView.as_view(), name='subscription_create'),
    path('create/success/', views.SubscriptionCreateSuccessView.as_view(), name='subscription_create_success'),
    path('test-add-to-basket/', views.what, name='what'),
    # path('create/confirm/', views.SubscriptionCreateConfirmView.as_view(), name='subscription_create_confirm'),
]

urlpatterns = [
    path(PREFIX, include(urls_no_prefix))
]