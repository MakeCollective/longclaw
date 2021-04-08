from django.db import models

from wagtail.snippets.models import register_snippet

from longclaw.shipping.models.locations import Address


@register_snippet
class Customer(models.Model):
    '''
    Hold details about a user. Details include at a minimum the amount of information
    to perform a transaction through Stripe
    '''
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
    

class Subscription(models.Model):
    pass


class SubscriptionOrder(models.Model):
    pass


class SubscriptionOrderItem(models.Model):
    pass
