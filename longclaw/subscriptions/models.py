from django.db import models
from django.conf import settings
from django.utils import timezone

from wagtail.snippets.models import register_snippet

from longclaw.settings import ORDER_MODEL

import datetime


@register_snippet
class Subscription(models.Model):
    ''' 
    Holds information relating to a single subscription
    '''
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    WEEKDAYS = (
        (MONDAY, 'Monday'), 
        (TUESDAY, 'Tuesday'), 
        (WEDNESDAY, 'Wednesday'), 
        (THURSDAY, 'Thursday'), 
        (FRIDAY, 'Friday'), 
        # (SATURDAY, 'Saturday'), 
        # (SUNDAY, 'Sunday'),
    )

    WEEKLY = 1
    EVERY_TWO_WEEKS = 2
    EVERY_THREE_WEEKS = 3
    EVERY_FOUR_WEEKS = 4
    DISPATCH_FREQUENCY_CHOICES = (
        (WEEKLY, 'Weekly'),
        (EVERY_TWO_WEEKS, 'Every 2 weeks'),
        (EVERY_THREE_WEEKS, 'Every 3 weeks'),
        (EVERY_FOUR_WEEKS, 'Every 4 weeks'),
    )
    
    account = models.ForeignKey('account.Account', related_name='subscriptions', on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_dispatch = models.DateField(blank=True, null=True)
    next_dispatch = models.DateField(blank=True, null=True)
    dispatch_count = models.IntegerField(default=0, help_text='The amount of times this Subscription has been dispatched')
    # repeat_weekly = models.BooleanField(default=False)
    # repeat_monthly = models.BooleanField(default=False)
    # repeat_period = models.IntegerField(blank=True, null=True, help_text='The amount of days until the order is to be repeated')
    dispatch_frequency = models.IntegerField(choices=DISPATCH_FREQUENCY_CHOICES, default=WEEKLY, help_text='The frequency of the order being fulfilled')
    dispatch_day_of_week = models.IntegerField(choices=WEEKDAYS, default=MONDAY)
    one_click_reminder = models.BooleanField(default=False, help_text='Whether or not to require a customer confirmation before dispatching the order')
    active = models.BooleanField(default=False, help_text='Whether or not this subscription should be dispatched as normal')
    shipping_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    selected_payment_method = models.ForeignKey('account.StripePaymentMethod', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_rate = models.ForeignKey('shipping.ShippingRate', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    @property
    def payment_method(self):
        if self.selected_payment_method:
            return self.selected_payment_method
        elif self.account and self.account.active_payment_method:
            return self.account.active_payment_method
        else:
            return None
    

    def __str__(self):
        return f'{self.id} - {self.account}'
    
    def activate(self):
        self.active = True
        self.save()
    
    def pause(self):
        self.active = False
        self.save()
    
    def update_next_dispatch(self, date):
        self.next_dispatch = date
        self.save()
    
    # def update_repeat_period(self, period):
    #     self.repeat_period = period
    #     self.save()

    def get_shipping_address(self):
        if not self.shipping_address:
            return self.subscription.shipping_address
        else:
            return self.shipping_address
    
    def get_billing_address(self):
        if not self.billing_address:
            return self.subscription.billing_address
        else:
            return self.billing_address
    
    def update_dispatch_date(self):
        self.last_dispatch = timezone.now()
        self.next_dispatch = timezone.now() + datetime.timedelta(weeks=self.dispatch_frequency)
        
        # Sanity check that the next_dispatch is the correct day of the week
        if self.next_dispatch.weekday() != self.dispatch_day_of_week:
            raise ValueError(f'next_dispatch day of week [{self.next_dispatch.weekday()}] doesn\'t match dispatch_day_of_week [{self.dispatch_day_of_week}]')
        
        self.save()
    
    def increment_dispatch_count(self):
        self.dispatch_count += 1
        self.save()
    

class SubscriptionOrderRelation(models.Model):
    subscription = models.ForeignKey('subscriptions.Subscription', related_name='+', on_delete=models.DO_NOTHING)
    order = models.ForeignKey(ORDER_MODEL, related_name='+', on_delete=models.DO_NOTHING)


class SubscriptionOrderItem(models.Model):
    '''
    An individual item model that holds quantity and a reference to the product variant
    '''
    product = models.ForeignKey(settings.PRODUCT_VARIANT_MODEL, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)
    subscription = models.ForeignKey('subscriptions.Subscription', related_name='items', on_delete=models.CASCADE)

    @property
    def total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.quantity} x {self.product.get_product_title()}'
