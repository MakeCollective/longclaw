from django.db import models
from django.conf import settings

from wagtail.snippets.models import register_snippet


@register_snippet
class Subscription(models.Model):
    ''' 
    Holds information relating to a single subscription
    '''
    account = models.ForeignKey('account.Account', related_name='subscriptions', on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_dispatch = models.DateTimeField(blank=True, null=True)
    next_dispatch = models.DateTimeField(blank=True, null=True)
    repeat_period = models.IntegerField(blank=True, null=True, help_text='The amount of days until the order is to be repeated')
    one_click_reminder = models.BooleanField(default=False, help_text='Whether or not to require a customer confirmation before dispatching the order')
    active = models.BooleanField(default=False, help_text='Whether or not this subscription should be dispatched as normal')
    shipping_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.account}'
    
    def activate(self):
        self.active = True
        self.save()
    
    def pause(self):
        self.active = False
        self.save()

    # def cancel(self):
    #     del self
    
    def update_next_dispatch(self, date):
        self.next_dispatch = date
        self.save()
    
    def update_repeat_period(self, period):
        self.repeat_period = period
        self.save()

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
    

class SubscriptionOrderRelation(models.Model):
    subscription = models.ForeignKey('subscriptions.Subscription', related_name='+', on_delete=models.DO_NOTHING)
    order = models.ForeignKey('orders.Order', related_name='+', on_delete=models.DO_NOTHING)


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
