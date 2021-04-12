from django.test import TestCase
from django.conf import settings
from django.apps import apps

from longclaw.subscriptions import (
    Subscription, SubscriptionOrder, SubscriptionOrderItem,
)


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


class SubscriptionOrderTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmore@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        subscription = Subscription.objects.create(
            customer=customer,
        )
        self.subscription_order = SubscriptionOrder.objects.create(
            # Don't think anything is required
            subscription=subscription,
        )
    
    def test_check_subscription_order_exists(self):
        assert isinstance(self.subscription_order, SubscriptionOrder)
    
    def test_check_default_status(self):
        assert self.subscription_order.status == SubscriptionOrder.SUBMITTED
    
    def test_fulfill(self):
        self.subscription_order.fulfill()
        assert self.subscription_order.status == SubscriptionOrder.FULFILLED
    
    def test_unfulfill(self):
        self.subscription_order.unfulfill()
        assert self.subscription_order.status == SubscriptionOrder.SUBMITTED
    
    def test_cancelled(self):
        self.subscription_order.cancel()
        assert self.subscription_order.status == SubscriptionOrder.CANCELLED


class SubscriptionOrderItemTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            name='Bloke Gilmoe',
            email='bloke_gilmore@make.nz',
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        subscription = Subscription.objects.create(
            customer=customer,
        )
        self.subscription_order = SubscriptionOrder.objects.create(
            # Don't think anything is required
            subscription=subscription,
        )

        product_variant_model = apps.get_model(
            app_label=settings.PRODUCT_VARIANT_MODEL.split('.')[0], 
            model_name=settings.PRODUCT_VARIANT_MODEL.split('.')[1]
        )

        home_page = Page.objects.first().get_children().first()
        test_product_model = product_variant_model._meta.get_field('product').related_model
        test_product = test_product_model(title='Test product', description='Test product')
        home_page.add_child(instance=test_product)
        test_product_variant = product_variant_model.objects.create(
            base_price=10,
            ref='test_product',
            stock=100,
            product=test_product,
        )
        self.subscription_order_item = SubscriptionOrderItem.objects.create(
            order=self.subscription_order,
            quantity=5,
            product=test_product_variant,
        )

    def test_check_subscription_order_item_exists(self):
        assert isinstance(self.subscription_order_item, SubscriptionOrderItem)

    def test_order_item_quantity(self):
        assert self.subscription_order_item.quantity == 5
    
    def test_order_item_total(self):
        self.subscription_order_item.quantity = 5
        self.subscription_order_item.product.base_price = 20
        assert self.subscription_order_item.total == 100
    
    def test_order_item_total2(self):
        assert self.subscription_order_item.total == self.subscription_order_item.quantity * self.subscription_order_item.product.price
    