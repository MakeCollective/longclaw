from django.urls import path
from longclaw.checkout import api, views
from longclaw.settings import API_URL_PREFIX

PREFIX = API_URL_PREFIX + 'checkout/'
urlpatterns = [
    path(PREFIX + '', api.capture_payment, name='longclaw_checkout'),
    path(PREFIX + 'prepaid/', api.create_order_with_token, name='longclaw_checkout_prepaid'),
    path(PREFIX + 'token/', api.create_token, name='longclaw_checkout_token'),
    path('checkout/', views.CheckoutView.as_view(), name='longclaw_checkout_view'),
    path('checkout/success/<int:pk>/', views.checkout_success, name='longclaw_checkout_success')
]
