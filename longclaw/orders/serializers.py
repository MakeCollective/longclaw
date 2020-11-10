from rest_framework import serializers
from longclaw.orders.models import OrderItem # Order
from longclaw.products.serializers import ProductVariantSerializer
from longclaw.shipping.serializers import AddressSerializer, GSSDeliveryRegionSerializer
from django.apps import apps
from longclaw.settings import ORDER_MODEL
Order = apps.get_model(*ORDER_MODEL.split('.'))

class OrderItemSerializer(serializers.ModelSerializer):

    product = ProductVariantSerializer()

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    shipping_address = AddressSerializer()
    total = serializers.SerializerMethodField()
    gss_delivery_region = GSSDeliveryRegionSerializer()

    def to_representation(self, value):
        rep = super().to_representation(value)
        rep['shipping_statuses'] = [choice for choice, _ in Order._meta.get_field('shipping_status').choices]
        return rep

    class Meta:
        model = Order
        fields = "__all__"

    def get_total(self, obj):
        return obj.total
