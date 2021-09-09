from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings

from longclaw.basket.utils import get_basket_items, destroy_basket
from longclaw.coupon.utils import discount_total
from longclaw.subscriptions.models import Subscription, SubscriptionOrderItem, SubscriptionOrderRelation
from longclaw.checkout.errors import PaymentError
from longclaw.settings import STRIPE_SECRET_KEY
from longclaw.configuration.models import Configuration

from django.apps import apps
from longclaw.settings import ORDER_MODEL
Order = apps.get_model(*ORDER_MODEL.split('.'))

from decimal import Decimal
import datetime
import stripe
import math

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
    shipping_rate=None,
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
        shipping_rate=shipping_rate,
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
    
    destroy_basket(request)

    return subscription


def dispatch_subscription_orders():
    '''
    Run through Subscriptions to find which ones are due to be dispatched today
    Create an Order from a Subscription
    Update the next dispatch date based on the Subscription dispatch_frequency

    While running through Subscriptions, if there are any that are marked "active",
    but are due to be dispatched on a PREVIOUS date, send an email to an admin
    to investigate
    '''

    # Find Subscriptions that are to be dispatched today
    due_subscriptions = Subscription.objects.filter(next_dispatch=timezone.now())

    # Create orders from subscriptions
    for subscription in due_subscriptions:
        order = create_order_from_subscription(subscription)
    
    check_erroneous_subscriptions()

    
def check_erroneous_subscriptions():
    '''
    Find any Subscriptions that should have been dispatched on a previous date
    that have not been completed
    '''
    erroneous_subscriptions = Subscription.objects.filter(next_dispatch__lt=timezone.now(), active=True)

    if erroneous_subscriptions.exists():
        id_list = list(erroneous_subscriptions.values_list('id', flat=True))
        # render_to_string('longclaw/subscriptions/erroneous_subscriptions.html', context={'erroneous_subscriptions': erroneous_subscriptions})
        # Send an email to admin or something?
        raise ValueError(f'Erroneous subscriptions, investigate these Subscription IDs: {id_list}')
        

def create_order_from_subscription(subscription):
    '''
    Create an Order from a Subscription
    Returns the created Order instance
    '''
    print('create_order_from_subscription')

    # Check that payment method is valid/active
    if not subscription.selected_payment_method.status == subscription.ACTIVE:
        print('Subscription payment method is not active')
        # Send an email to admin
        return None

    # Figure out shipping cost
    if subscription.shipping_rate:
        shipping_rate = subscription.shipping_rate.rate
    else:
        # Shouldn't come to to this
        shipping_rate = 0

    order = Order(
        account=subscription.account,
        email=subscription.account.email,
        shipping_address=subscription.shipping_address,
        billing_address=subscription.billing_address,
        shipping_rate=shipping_rate,
    )
    order.save()

    # Create the order items & compute total
    total = 0
    for subscription_item in subscription.items.all():
        item = subscription_item.product
        quantity = subscription_item.quantity
        total += subscription_item.total
        order_item = order.items.create(
            product=item,
            base_product_id=item.product.id,
            product_variant_id=item.id,
            product_variant_price=item.price,
            product_variant_ref=item.ref,
            product_variant_title=item.get_product_title(),
            quantity=quantity,
            order=order,
        )
        # order_item.save()

    payment_amount = total + shipping_rate
    currency = Configuration.objects.first().currency
    description = 'Payment from {} for order id #{}'.format(subscription.account.email, order.id)

    # Create a Stripe payment using the saved PaymentMethod from the subscription
    stripe.api_key = STRIPE_SECRET_KEY

    try:
        stripe_payment_intent = stripe.PaymentIntent.create(
            amount=int(math.ceil(payment_amount * 100)),
            currency=currency,
            customer=subscription.account.stripe_customer_id,
            payment_method=subscription.selected_payment_method,
            description=description,
            confirm=True, # The same as creating and confirming a PaymentIntent in the same step
        )
    except PaymentError as e:
        order.status = order.FAILURE
        order.status_note = str(e)
    except Exception as e:
        print('Some unexpected error')
        raise e
    else:
        order.payment_date = timezone.now()
        order.transaction_id = stripe_payment_intent.id
    
    order.save()

    # Move next dispatch date
    subscription.update_dispatch_date()
    subscription.increment_dispatch_count()
    
    return order
