from django.urls import path
from longclaw.shipping import api
from longclaw.settings import API_URL_PREFIX

address_list = api.AddressViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
address_detail = api.AddressViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

ADDRESS_PREFIX = API_URL_PREFIX + 'addresses/'
SHIPPING_PREFIX = API_URL_PREFIX + 'shipping/'
urlpatterns = [
    # path(ADDRESS_PREFIX + '', address_list, name='longclaw_address_list'),
    # path(ADDRESS_PREFIX + '<int:pk>/', address_detail, name='longclaw_address_detail'),
    path(SHIPPING_PREFIX + 'cost/', api.shipping_cost, name='longclaw_shipping_cost'),
    path(SHIPPING_PREFIX + 'countries/', api.shipping_countries, name='longclaw_shipping_countries'),
    path(SHIPPING_PREFIX + 'countries/<slug:country>/', api.shipping_options, name='longclaw_shipping_options'),
    path(SHIPPING_PREFIX + 'options/', api.shipping_options, name='longclaw_applicable_shipping_rate_list')
]
