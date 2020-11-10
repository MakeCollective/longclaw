from rest_framework.decorators import action 
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
# from longclaw.orders.models import Order
from longclaw.orders.serializers import OrderSerializer
from django.apps import apps
from longclaw.settings import ORDER_MODEL
Order = apps.get_model(*ORDER_MODEL.split('.'))


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()

    @action(detail=True, methods=['post'])
    def refund_order(self, request, pk):
        """Refund the order specified by the pk
        """
        order = Order.objects.get(id=pk)
        order.refund()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def fulfill_order(self, request, pk):
        """Mark the order specified by pk as fulfilled
        """
        order = Order.objects.get(id=pk)
        order.fulfill()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def send_to_gss(self, request, pk):
        order = Order.objects.get(id=pk)
        order.send_to_gss()
        return Response(status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def update_shipping_status(self, request, pk, shipping_status):
        order = Order.objects.get(id=pk)
        order.update_shipping_status(shipping_status)
        return Response(status.HTTP_204_NO_CONTENT)
