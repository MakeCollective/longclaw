from django.test import TestCase

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
    


# name = models.CharField(max_length=64)
# line_1 = models.CharField(max_length=128)
# line_2 = models.CharField(max_length=128, blank=True)
# city = models.CharField(max_length=64)
# postcode = models.CharField(max_length=10)
# cou