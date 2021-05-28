from django.urls import path
from longclaw.coupon import views
from longclaw.settings import API_URL_PREFIX

PREFIX = API_URL_PREFIX + 'coupon/'
urlpatterns = [
    path(PREFIX + 'verify-discount-code/', views.verify_discount_code, name='verify_discount_code'),
    path(PREFIX + 'remove-basket-discount/', views.remove_basket_discount, name='remove_basket_discount')
]
