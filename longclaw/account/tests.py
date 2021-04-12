from django.test import TestCase
from django.conf import settings
from django.apps import apps

from wagtail.core.models import Page

from longclaw.shipping.models.locations import Address, Country
from longclaw.account.models import (
    Account, AccountPaymentMethod,
    
)


class AccountTestCase(TestCase):
    def setUp(self):
        country = Country.objects.create(
            iso='NZ',
            name_official='New Zealand',
            name='New Zealand',
        )
        address = Address.objects.create(
            name='Jeff Tester', 
            line_1='4a Valley Road', 
            city='Christchurch', 
            postcode='8011', 
            country=country,
        )
        Account.objects.create(
            name='Jeff Tester',
            email='jeff_tester@make.nz',
            phone='0212345678',
            company_name='Make Collective',
            shipping_address=address,
            billing_address=address,
            stripe_customer_id=None,
            active_payment_method=None,
        )

    def test_account_exists(self):
        account = Account.objects.get(name='Jeff Tester')
    

class AccountPaymentMethodTestCase(TestCase):
    def setUp(self):
        account = Account.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmoe@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_JGFFKICO07bpLL',
        )
        self.account_payment_method = AccountPaymentMethod.objects.create(
            account=account,
            name='Test payment method',
            stripe_id='pm_1IdikrHdGXKihVkiz44IHKkr',
        )

    def test_payment_method_exists(self):
        self.account_payment_method.check_valid()


class MissingStripeSecretTestCase(TestCase):
    ''' This test case kind of relies on that Stripe has been pip installed '''
    def setUp(self):
        account = Account.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmoe@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        self.account_payment_method = AccountPaymentMethod.objects.create(
            account=account,
            name='Test payment method',
            stripe_id='pm_abc123',
        )

    def test_missing_stripe_key(self):
        del settings.STRIPE_SECRET
        self.assertRaises(AttributeError, self.account_payment_method.check_valid)

    def test_empty_stripe_key(self):
        settings.STRIPE_SECRET = ''
        self.assertRaises(ValueError, self.account_payment_method.check_valid)


