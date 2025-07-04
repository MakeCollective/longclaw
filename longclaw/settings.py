"""
Default settings for longclaw apps
"""
from django.conf import settings

# The payment gateway backend to use
# Can be 'longclaw.checkout.gateways.braintree.BraintreePayment',
# 'longclaw.checkout.gateways.braintree.PaypalVZeroPayment',
# 'longclaw.checkout.gateways.stripe.StripePayment' or 'longclaw.checkout.gateways.BasePayment'
# Or a custom implementation
PAYMENT_GATEWAY = getattr(settings,
                          'PAYMENT_GATEWAY',
                          'longclaw.checkout.gateways.base.BasePayment')

# The product variant model to use. This allows custom implementations of
# product models.
PRODUCT_VARIANT_MODEL = getattr(
    settings, 'PRODUCT_VARIANT_MODEL', 'products.ProductVariantBase')

# The order model to use. This allows custom implementation of order models
ORDER_MODEL = getattr(
    settings, 'ORDER_MODEL', 'orders.Order')

ORDER_LIST_VIEW_URL = '/admin/orders/order/'

# Only required if using Stripe as the payment gateway
STRIPE_PUBLIC_KEY = getattr(settings, 'STRIBE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', '')

# Only required if using Braintree as the payment gateway
BRAINTREE_SANDBOX = getattr(settings, 'BRAINTREE_SANDBOX', False)
BRAINTREE_MERCHANT_ID = getattr(settings, 'BRAINTREE_MERCHANT_ID', '')
BRAINTREE_PUBLIC_KEY = getattr(settings, 'BRAINTREE_PUBLIC_KEY', '')
BRAINTREE_PRIVATE_KEY = getattr(settings, 'BRAINTREE_PRIVATE_KEY', '')

# Only required for using paypal as the payment gateway through braintree v.zero
VZERO_ACCESS_TOKEN = getattr(settings, 'VZERO_ACCESS_TOKEN', '')

API_URL_PREFIX = getattr(settings, 'LONGCLAW_API_URL_PREFIX', 'api/')
