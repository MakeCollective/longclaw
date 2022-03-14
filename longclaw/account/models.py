from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet


class Account(models.Model):
    '''
    Hold details about a user. Details include at a minimum the amount of information
    to perform a transaction through Stripe
    '''
    user = models.OneToOneField(User, related_name='account', on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('shipping.Address', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_billing_address_same = models.BooleanField(default=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    active_payment_method = models.OneToOneField('account.PaymentMethod', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

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

    @property
    def stripe_active_payment_method(self):
        if not self.active_payment_method:
            return None
        try:
            pm = StripePaymentMethod.objects.get(id=self.active_payment_method.id)
        except StripePaymentMethod.DoesNotExist as e:
            raise e
        else:
            return pm

    # Related fields
    # AccountPaymentMethod(s)
    # Future proofing in case an Account will have multiple payment methods (cards)

    panels = [
        SnippetChooserPanel('user'),
        FieldPanel('phone'),
        FieldPanel('company_name'),
        SnippetChooserPanel('shipping_address'),
        SnippetChooserPanel('billing_address'),
        FieldPanel('shipping_billing_address_same'),
        FieldPanel('stripe_customer_id'),
        SnippetChooserPanel('active_payment_method'),
    ]

class PaymentMethod(models.Model):
    '''
    Hold details about an Account's (potentially) multiple payment methods (cards)
    Must be attached to an Account. If the attached Account is deleted, so are it's related PaymentMethods
    '''
    ACTIVE = 1
    DEACTIVATED = 2
    INVALID = 3
    EXPIRED = 4
    STATUSES = (
        (ACTIVE, 'Active'),
        (DEACTIVATED, 'Deactivated'),
        (INVALID, 'Invalid'),
        (EXPIRED, 'Expired'),
    )
    
    account = models.ForeignKey('account.Account', related_name='payment_methods', on_delete=models.CASCADE)
    label = models.CharField(max_length=255, help_text='User friendly label for the payment method', blank=True, null=True)
    status = models.IntegerField(default=ACTIVE, choices=STATUSES, help_text='Status to show if the PaymentMethod is active/deactive or otherwise')
    
    def __str__(self):
        if self.label:
            return self.label
        else:
            return f'{str(self.account)} - PaymentMethod ID: {self.id}'

    def check_valid(self):
        raise NotImplementedError

    @property
    def is_active_payment_method(self):
        if self.id and self.account and self.account.active_payment_method:
            return self.id == self.account.active_payment_method.id
        else:
            return False

    def deactivate(self):
        self.status = self.DEACTIVATED
        self.save()
        return self
    
    def is_valid(self):
        return self.status == self.ACTIVE
    

class StripePaymentMethod(PaymentMethod):
    '''
    A subclass of the PaymentMethod
    Holds Stripe specific fields
    '''
    name = models.CharField(max_length=255, blank=True, null=True)
    stripe_id = models.CharField(max_length=255)
    last4 = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=255, help_text='Will most likely be "card"')
    exp_month = models.CharField(max_length=255)
    exp_year = models.CharField(max_length=255)

    def check_valid(self):
        try:
            import stripe
        except Exception as e:
            raise e

        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not stripe.api_key:
            raise ValueError('STRIPE_SECRET_KEY has not been provided')
        
        try:
            pm = stripe.PaymentMethod.retrieve(self.stripe_id)
        except Exception as e:
            raise e

        return True

    def __str__(self):
        if self.label:
            return self.label
        elif self.name:
            return self.name
        else:
            return f'{self.last4}, {self.exp_month}/{self.exp_year}'
