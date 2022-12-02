from django.db import models
from django.conf import settings
from django.utils import timezone

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
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
    
    account = models.ForeignKey('account.Account', related_name='subscriptions', on_delete=models.CASCADE)
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
    pause_until_date = models.DateField(blank=True, null=True)

    @property
    def payment_method(self):
        if self.selected_payment_method:
            return self.selected_payment_method
        elif self.account and self.account.active_payment_method:
            return self.account.active_payment_method
        else:
            return None
    
    @property
    def paused(self):
        if not self.pause_until_date:
            return False
        return timezone.localtime(timezone.now()).date() < self.pause_until_date

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

    def update_dispatch_day_of_week(self, new_weekday):
        self.dispatch_day_of_week = new_weekday
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
        self.last_dispatch = timezone.localdate(timezone.now())
        self.next_dispatch = self.get_next_dispatch_date()

        # Sanity check that the next_dispatch is the correct day of the week
        if self.next_dispatch.weekday() != self.dispatch_day_of_week:
            raise ValueError(f'[Subscription ID: {self.id}] next_dispatch day of week [{self.next_dispatch.weekday()}] doesn\'t match dispatch_day_of_week [{self.dispatch_day_of_week}]')

        self.save()
    
    def next_weekday(self, d, weekday, frequency=1, same_day_acceptable=False):
        ''' Adjust this if desired to allow Order to be dispatched on same day as Subscription created... maybe? '''
        days_ahead = weekday - d.weekday()
        if not same_day_acceptable:
            if days_ahead <= 0: # Target day already happened this week
                days_ahead += 7
        else:
            if days_ahead < 0:
                days_ahead += 7
        
        if frequency > 0:
            days_ahead += 7 * (frequency - 1)

        return d + datetime.timedelta(days_ahead)

    def get_next_dispatch_date(self, from_date=None):
        if not from_date:
            from_date = timezone.localdate(timezone.now())
        
        # if not self.paused # TODO logic for paused_until date
        if self.last_dispatch:
            next_dispatch_date = self.next_weekday(
                from_date, 
                self.dispatch_day_of_week,
                frequency=self.dispatch_frequency,
            )
        else:
            next_dispatch_date = self.next_weekday(
                from_date,
                self.dispatch_day_of_week,
            )
        return next_dispatch_date
    
    def increment_dispatch_count(self):
        self.dispatch_count += 1
        self.save()
    
    def update_fields(self, **kwargs):
        ''' Update the fields provided in kwargs '''
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()
    
    def next_dispatch_after_pause(self):
        ''' Finds the next dispatch date after a pause period has ended '''
        # Check if there is a pause_until_date, and is in future
        today = timezone.localtime(timezone.now()).date()
        if self.pause_until_date and self.pause_until_date > today:
            # If next_dispatch was meant to happen after the pause date anyway - use that one
            if self.pause_until_date and self.pause_until_date <= self.next_dispatch:
                return self.next_dispatch
            # Otherwise, find the next weekday after the end of the puase date
            return self.next_weekday(self.pause_until_date, self.dispatch_day_of_week)
        else:
            # If no pause_until_date, or it has already passed, then get the existing next_dispatch
            return self.next_dispatch
    

    panels = [
        SnippetChooserPanel('account'),
        FieldPanel('last_dispatch'),
        FieldPanel('next_dispatch'),
        FieldPanel('dispatch_count'),
        FieldPanel('dispatch_frequency'),
        FieldPanel('dispatch_day_of_week'),
        FieldPanel('one_click_reminder'),
        FieldPanel('active'),
        SnippetChooserPanel('shipping_address'),
        SnippetChooserPanel('billing_address'),
        SnippetChooserPanel('selected_payment_method'),
        SnippetChooserPanel('shipping_rate'),
        FieldPanel('pause_until_date'),
    ]


class SubscriptionOrderItem(models.Model):
    '''
    An individual item model that holds quantity and a reference to the product variant
    '''
    product = models.ForeignKey(settings.PRODUCT_VARIANT_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=1)
    subscription = models.ForeignKey('subscriptions.Subscription', related_name='items', on_delete=models.CASCADE)

    @property
    def total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.quantity} x {self.product.get_product_title()}'
