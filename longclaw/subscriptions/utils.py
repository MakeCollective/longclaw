from decimal import Decimal
from django.utils import timezone
from decimal import Decimal

from longclaw.basket.utils import get_basket_items, destroy_basket
from longclaw.coupon.utils import discount_total
from longclaw.subscriptions.models import Subscription, SubscriptionOrderItem, SubscriptionOrderRelation

import datetime


def next_weekday(d, weekday):
    ''' Adjust this if desired to allow Order to be dispatched on same day as Subscription created... maybe? '''
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def create_subscription_order(
    request,
    account,
    shipping_address=None,
    billing_address=None,
    dispatch_frequency=None,
    dispatch_day_of_week=None,
    selected_payment_method=None,
    shipping_option=None,
    discount=None):
    """
    Create an order from a basket and customer infomation
    """
    basket_items, current_basket_id = get_basket_items(request)

    if not basket_items:
        raise ValueError('Basket is empty, do not complete order')

    if not dispatch_frequency:
        raise ValueError('Dispatch frequency must be set. How often an Order is dispatched is required')
    
    if not selected_payment_method:
        raise ValueError('A payment method must be selected before a subscription is created')
    
    if not selected_payment_method.is_valid():
        raise ValueError('A valid payment method must be provided, check your payment method')
    
    dispatch_day_of_week = int(dispatch_day_of_week)


    # If no address(es) provided, use defualt account settings
    if not shipping_address:
        shipping_address = account.shipping_address

    if not billing_address:
        billing_address = account.shipping_address

    # Get date of next day of the week selected
    today = timezone.now()
    next_weekday_selected = next_weekday(today, dispatch_day_of_week)

    subscription = Subscription(
        account=account,
        shipping_address=shipping_address,
        billing_address=billing_address,
        dispatch_frequency=dispatch_frequency,
        dispatch_day_of_week=dispatch_day_of_week,
        selected_payment_method=selected_payment_method,
        next_dispatch=next_weekday_selected,
        active=True,
    )
    subscription.save()

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

    return subscription
