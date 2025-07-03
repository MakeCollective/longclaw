from django.urls import path
from longclaw.orders import api

from longclaw.settings import API_URL_PREFIX

from . import views

orders = api.OrderViewSet.as_view({
    'get': 'retrieve'
})

fulfill_order = api.OrderViewSet.as_view({
    'post': 'fulfill_order'
})

unfulfill_order = api.OrderViewSet.as_view({
    'post': 'unfulfill_order'
})

refund_order = api.OrderViewSet.as_view({
    'post': 'refund_order'
})

get_all_orders = api.OrderViewSet.as_view({
    'get': 'list'
})

order_statuses = api.OrderViewSet.as_view({
    'get': 'order_statuses'
})

set_order_status = api.OrderViewSet.as_view({
    'post': 'set_order_status'
})


PREFIX = API_URL_PREFIX + 'order/'
urlpatterns = [
    path(PREFIX + 'statuses/', order_statuses, name='longclaw_order_statuses'),
    path(PREFIX + '<int:pk>/status/<int:status_code>/', set_order_status, name='longclaw_set_order_status'),
    path(PREFIX + '<int:pk>/', orders, name='longclaw_orders'),
    path(PREFIX + '<int:pk>/fulfill/', fulfill_order, name='longclaw_fulfill_order'),
    path(PREFIX + '<int:pk>/unfulfill/', unfulfill_order, name='longclaw_unfulfill_order'),
    path(PREFIX + '<int:pk>/refund/', refund_order, name='longclaw_refund_order'),
    path(PREFIX, get_all_orders, name='longclaw_all_orders'),
    path('test-add-to-basket/', views.test_add_to_basket, name='test_add_to_basket'),
]
