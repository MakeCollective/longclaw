from django.test import TestCase
from django.conf import settings

from longclaw.shipping.models.locations import Address, Country
from longclaw.customer.models import (
    Customer, CustomerPaymentMethod,
    Subscription, SubscriptionOrder, SubscriptionOrderItem,
)


class CustomerTestCase(TestCase):
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
        Customer.objects.create(
            name='Jeff Tester',
            email='jeff_tester@make.nz',
            phone='0212345678',
            company_name='Make Collective',
            shipping_address=address,
            billing_address=address,
            stripe_customer_id=None,
            active_payment_method=None,
        )

    def test_customer_exists(self):
        customer = Customer.objects.get(name='Jeff Tester')
    

class CustomerPaymentMethodTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmoe@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_JGFFKICO07bpLL',
        )
        self.customer_payment_method = CustomerPaymentMethod.objects.create(
            customer=customer,
            name='Test payment method',
            stripe_id='pm_1IdikrHdGXKihVkiz44IHKkr',
        )

    def test_payment_method_exists(self):
        self.customer_payment_method.check_valid()


class MissingStripeSecretTestCase(TestCase):
    ''' This test case kind of relies on that Stripe has been pip installed '''
    def setUp(self):
        customer = Customer.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmoe@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        self.customer_payment_method = CustomerPaymentMethod.objects.create(
            customer=customer,
            name='Test payment method',
            stripe_id='pm_abc123',
        )

    def test_missing_stripe_key(self):
        del settings.STRIPE_SECRET
        self.assertRaises(AttributeError, self.customer_payment_method.check_valid)

    def test_empty_stripe_key(self):
        settings.STRIPE_SECRET = ''
        self.assertRaises(ValueError, self.customer_payment_method.check_valid)


class SubscriptionTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmoe@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        self.subscription = Subscription.objects.create(
            customer=customer,
        )
    
    def test_check_subscription_exists(self):
        assert isinstance(self.subscription, Subscription)