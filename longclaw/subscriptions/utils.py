from decimal import Decimal
from django.utils.module_loading import import_string
from django.utils import timezone
from ipware.ip import get_real_ip
from decimal import Decimal

from longclaw.basket.utils import get_basket_items, destroy_basket
from longclaw.shipping.utils import get_shipping_cost
from longclaw.coupon.utils import discount_total
from longclaw.orders.models import Order, OrderItem
from longclaw.shipping.models import Address
from longclaw.configuration.models import Configuration
from longclaw.subscriptions.models import Subscription, SubscriptionOrderItem, SubscriptionOrderRelation

def create_subscription_order(
    request,
    account,
    shipping_address=None,
    billing_address=None,
    shipping_option=None,
    discount=None):
    """
    Create an order from a basket and customer infomation
    """
    print('*'*80)
    print('create_subscription_order')
    print('*'*80)
    basket_items, current_basket_id = get_basket_items(request)

    if not basket_items:
        raise ValueError('Basket is empty, do not complete order')


    # If no address(es) provided, use defualt account settings
    if not shipping_address:
        shipping_address = account.shipping_address

    if not billing_address:
        billing_address = account.shipping_address
    

    ip_address = get_real_ip(request)
    # if shipping_country and shipping_option:
    #     site_settings = Configuration.for_request(request)
    #     shipping_rate = get_shipping_cost(
    #         site_settings,
    #         shipping_address.country.pk,
    #         shipping_option,
    #         basket_id=current_basket_id,
    #         destination=shipping_address,
    #     )['rate']
    # else:
    #     shipping_rate = Decimal(0)
    shipping_rate = Decimal(0)

    order = Order(
        email=account.user.email,
        ip_address=ip_address,
        shipping_address=shipping_address,
        billing_address=billing_address,
        shipping_rate=shipping_rate,
        discount=discount,
    )
    order.save()

    subscription = Subscription(
        account=account,
        shipping_address=shipping_address,
        billing_address=billing_address,
    )

    # Create the order items & compute total
    total = 0
    for item in basket_items:
        total += item.total()
        order_item = SubscriptionOrderItem(
            product=item.variant,
            quantity=item.quantity,
            subscription=subscription
        )
        order_item.save()
    
    # Set the relative discount instance (if it exists) to refer to the order
    if discount:
        # last second check that the discount code can still be used
        if not discount.coupon.depleted:
            # Adjust the total by the discount
            total, _ = discount_total(total, discount)
            total = Decimal(total)

    # if capture_payment:
    #     desc = 'Payment from {} for order id #{}'.format(email, order.id)
    #     try:
    #         transaction_id = GATEWAY.create_payment(request,
    #                                                 total + shipping_rate,
    #                                                 description=desc)
    #         order.payment_date = timezone.now()
    #         order.transaction_id = transaction_id

    #         # Payment has succeeded, so consume the discount code used
    #         if discount:
    #             if not discount.coupon.depleted:
    #                 discount.consume(order)
            
    #         # Once the order has been successfully taken, we can empty the basket
    #         destroy_basket(request)
    #     except PaymentError as e:
    #         order.status = order.FAILURE
    #         order.status_note = str(e)

    #     order.save()

    return order
