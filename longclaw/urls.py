from django.conf.urls import include, url
from longclaw.basket import urls as basket_urls
from longclaw.checkout import urls as checkout_urls
from longclaw.shipping import urls as shipping_urls
from longclaw.orders import urls as order_urls
from longclaw.coupon import urls as coupon_urls
from longclaw.account import urls as account_urls
from longclaw.subscriptions import urls as subscription_urls

urlpatterns = [
    url(r'', include(basket_urls)),
    url(r'', include(checkout_urls)),
    url(r'', include(shipping_urls)),
    url(r'', include(order_urls)),
    url(r'', include(coupon_urls)),
    url(r'', include(account_urls)),
    url(r'', include(subscription_urls)),
]
