from django.test import TestCase
from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model

from wagtail.core.models import Page

from longclaw.account.models import Account
from longclaw.subscriptions.models import (
    Subscription, SubscriptionOrderItem,
)
from longclaw.orders.models import Order

UserModel = get_user_model()

class SubscriptionTestCase(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user(
            username='blake',
            email='blake@make.nz',
            password='testpassword123',
            is_active=True,
        )
        account = Account.objects.create(
            user=user,
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        self.subscription = Subscription.objects.create(
            account=account,
        )
    
    def test_check_subscription_exists(self):
        assert isinstance(self.subscription, Subscription)


class SubscriptionOrderTestCase(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user(
            username='blake',
            email='blake@make.nz',
            password='testpassword123',
            is_active=True,
        )
        account = Account.objects.create(
            user=user,
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        subscription = Subscription.objects.create(
            account=account,
        )
        order = Order.objects.create()
        # self.subscription_order_relation = SubscriptionOrderRelation.objects.create(
        #     # Don't think anything is required
        #     subscription=subscription,
        #     order=order,
        # )
    
    # def test_check_subscription_order_exists(self):
    #     assert isinstance(self.subscription_order_relation, SubscriptionOrderRelation)


class SubscriptionOrderItemTestCase(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user(
            username='blake',
            email='blake@make.nz',
            password='testpassword123',
            is_active=True,
        )
        account = Account.objects.create(
            user=user,
            phone='0212345678',
            stripe_customer_id='cus_abc123',
        )
        subscription = Subscription.objects.create(
            account=account,
        )
        order = Order.objects.create()
        # self.subscription_order_relation = SubscriptionOrderRelation.objects.create(
        #     # Don't think anything is required
        #     subscription=subscription,
        #     order=order,
        # )

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
            subscription=subscription,
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
    