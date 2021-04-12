from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from wagtail.snippets.models import register_snippet

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
    '''
    Hold Order specific information and be the model to relate the OrderItems to.
    Has a one-to-one relationship with a Subscription.
    '''
    SUBMITTED = 1
    FULFILLED = 2
    CANCELLED = 3
    REFUNDED = 4
    FAILURE = 5
    ORDER_STATUSES = (
        (SUBMITTED, 'Submitted'),
        (FULFILLED, 'Fulfilled'),
        (CANCELLED, 'Cancelled'),
        (REFUNDED, 'Refunded'),
        (FAILURE, 'Payment Failed')
    )
    
    subscription = models.OneToOneField('customer.Subscription', related_name='subscription_order', on_delete=models.CASCADE)
    
    payment_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ORDER_STATUSES, default=SUBMITTED)
    status_note = models.CharField(max_length=128, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    # contact info
    email = models.EmailField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    # shipping address
    # can have a shipping address specific to the order, will default to the Customer's
    # shipping address if one is not set, same with billing address
    # shipping info
    shipping_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    # billing info
    billing_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    shipping_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'Order #{self.id} - {self.email}'
    
    @property
    def total(self):
        '''
        Total cost of the order
        '''
        total = 0
        for item in self.items.all():
            total += item.total
        return round(total, 2)

    @property
    def final_payment(self):
        '''
        The total payment received
        This includes the total price (reduced by any discount applied), plus shipping
        '''
        total = self.total
        if self.shipping_rate:
            total += self.shipping_rate
        if self.discounts.first():
            total, _ = discount_total(total, self.discounts.first())
        return round(total, 2)

    @property
    def total_items(self):
        '''
        The number of individual items on the order
        '''
        return self.items.count()
    
    def refund(self):
        '''
        TODO
        '''
        pass

    def fulfill(self):
        '''
        Mark this order as being fulfilled
        '''
        self.status = self.FULFILLED
        self.save()
    
    def unfulfill(self):
        '''
        Unmark this order as being fulfilled, set it back to the default (Submitted)
        '''
        self.status = self.SUBMITTED
        self.save()
    
    def cancel(self, refund=True):
        '''
        Cancel this order, optionally refunding it
        '''
        if refund:
            self.refund()
        self.status = self.CANCELLED
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


class SubscriptionOrderItem(models.Model):
    '''
    An individual item model that holds quantity and a reference to the product variant
    '''
    product = models.ForeignKey(settings.PRODUCT_VARIANT_MODEL, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)
    order = models.ForeignKey('customer.SubscriptionOrder', related_name='items', on_delete=models.CASCADE)

    @property
    def total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.quantity} x {self.product.get_product_title()}'
