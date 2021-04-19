from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from wagtail.snippets.models import register_snippet


@register_snippet
class Account(models.Model):
    '''
    Hold details about a user. Details include at a minimum the amount of information
    to perform a transaction through Stripe
    '''
    user = models.OneToOneField(User, related_name='account', on_delete=models.SET_NULL, blank=True, null=True) # one to one
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    active_payment_method = models.ForeignKey('account.AccountPaymentMethod', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        string = f'({self.id}) '
        if not self.user:
            string += f'No User attached'
        else:
            string += f'{self.user.email}'
        return string

    @property
    def name(self):
        full_name = []
        if self.user.first_name:
            full_name.append(self.user.first_name)
        if self.user.last_name:
            full_name.append(self.user.last_name)
        return ' '.join(full_name)
    
    @property
    def email(self):
        return self.user.email

    # Related fields
    # AccountPaymentMethod(s)
    # Future proofing in case an Account will have multiple payment methods (cards)


class AccountPaymentMethod(models.Model):
    '''
    Hold details about an Account's (potentially) multiple payment methods (cards)
    Must be attached to an Account. If the attached Account is deleted, so are it's related PaymentMethods
    '''
    account = models.ForeignKey('account.Account', related_name='payment_methods', on_delete=models.CASCADE)
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
    