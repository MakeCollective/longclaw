from rest_framework import serializers
from longclaw.orders.models import OrderItem
from longclaw.coupon.models import Discount
from longclaw.coupon.utils import discount_total
from longclaw.products.serializers import ProductVariantSerializer
from longclaw.shipping.serializers import AddressSerializer

from django.apps import apps
from longclaw.settings import ORDER_MODEL
Order = apps.get_model(*ORDER_MODEL.split('.'))


class OrderItemSerializer(serializers.ModelSerializer):

    product = ProductVariantSerializer()
    total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    shipping_address = AddressSerializer()
    total = serializers.SerializerMethodField()
    order_count = serializers.ReadOnlyField()

    def to_representation(self, value):
        rep = super().to_representation(value)
        try:
            discount = Discount.objects.get(order=value.id)
            rep['discount_total'], amount_off = discount_total(value.total + value.shipping_rate, discount)
            rep['discount_value'] = discount.coupon.discount_string(discount.coupon.discount_value)
        except Discount.DoesNotExist:
            rep['discount_total'] = None
            rep['discount_value'] = None

        discount_amount = value.discount_amount()
        if discount_amount:
            rep['discount_amount'] = discount_amount
        else:
            rep['discount_amount'] = None
        
        rep['coupon_code'] = None
        if value.discounts.exists():
            try:
                rep['coupon_code'] = value.discounts.first().coupon.code
            except Exception as e:
                pass
        
        return rep

    class Meta:
        model = Order
        fields = "__all__"

    def get_total(self, obj):
        return obj.total
