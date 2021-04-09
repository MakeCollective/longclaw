from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from wagtail.snippets.models import register_snippet

from datetime import datetime

from longclaw.shipping.models.locations import Address


@register_snippet
class Customer(models.Model):
    '''
    Hold details about a user. Details include at a minimum the amount of information
    to perform a transaction through Stripe
    '''
    user = models.ForeignKey(User, related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    active_payment_method = models.ForeignKey('customer.CustomerPaymentMethod', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    # Related fields
    # CustomerPaymentMethod(s)
    # Future proofing in case a Customer will have multiple payment methods (cards)


class CustomerPaymentMethod(models.Model):
    '''
    Hold details about a Customer's (potentially) multiple payment methods (cards)
    Must be attached to a Customer. If the attached Customer is deleted, so are it's related PaymentMethods
    '''
    customer = models.ForeignKey('customer.Customer', related_name='payment_methods', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text='User friendly name for the payment method')
    stripe_id = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'

    def check_valid(self):
        try:
            import stripe
        except Exception as e:
            raise e

        stripe.api_key = settings.STRIPE_SECRET
        if not stripe.api_key:
            raise ValueError('STRIPE_SECRET has not been provided')
        
        try:
            pm = stripe.PaymentMethod.retrieve(self.stripe_id)
        except Exception as e:
            raise e

        return True
    

class Subscription(models.Model):
    ''' 
    Holds information relating to a single subscription

    '''
    customer = models.ForeignKey('customer.Customer', related_name='subscriptions', on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_dispatch = models.DateTimeField(blank=True, null=True)
    next_dispatch = models.DateTimeField(blank=True, null=True)
    repeat_period = models.IntegerField(blank=True, null=True, help_text='The amount of days until the order is to be repeated')
    one_click_reminder = models.BooleanField(default=False, help_text='Whether or not to require a customer confirmation before dispatching the order')
    subscription_order = models.ForeignKey('customer.SubscriptionOrder', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    active = models.BooleanField(default=False, help_text='Whether or not this subscription should be dispatched as normal')

    def __str__(self):
        return f'{self.id} - {self.customer}'
    
    def activate(self):
        self.active = True
        self.save()
    
    def cancel(self):
        self.active = False
        self.save()
    
    def update_next_dispatch(self, date):
        self.next_dispatch = date
        self.save()
    
    def update_repeat_period(self, period):
        self.repeat_period = period
        self.save()
    

    

class SubscriptionOrder(models.Model):
    pass


class SubscriptionOrderItem(models.Model):
    pass
