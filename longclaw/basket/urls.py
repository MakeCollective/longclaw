from django.urls import path
from longclaw.basket import api
from longclaw.basket import views
from longclaw.settings import API_URL_PREFIX

basket_list = api.BasketViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'bulk_update'
})

basket_detail = api.BasketViewSet.as_view({
    'delete': 'destroy'
})

item_count = api.BasketViewSet.as_view({
    'get': 'item_count'
})

total_items = api.BasketViewSet.as_view({
    'get': 'total_items'
})

PREFIX = API_URL_PREFIX + 'basket/'
urlpatterns = [
    path('basket/', views.BasketView.as_view(), name='longclaw_basket'),
    path(PREFIX, basket_list, name='longclaw_basket_list'),
    path(PREFIX + 'count/', total_items, name='longclaw_basket_total_items'),
    path(PREFIX + '<int:variant_id>/', basket_detail, name='longclaw_basket_detail'),
    path(PREFIX + '<int:variant_id>/count/', item_count, name='longclaw_basket_item_count'),
]
