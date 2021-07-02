from rest_framework.decorators import action 
from rest_framework import permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from longclaw.orders.models import Order
from longclaw.orders.serializers import OrderSerializer

from collections import OrderedDict


class OrderLimitOffsetPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):

        count = self.count
        next_link = self.get_next_link()
        next_params = {'limit': self.limit, 'offset': min(self.offset + self.limit, self.count)}
        previous_link = self.get_previous_link()
        previous_params = {'limit': self.limit, 'offset': max(self.offset - self.limit, 0)}

        od = OrderedDict([
            ('count', count),
            ('next', next_link),
        ])
        
        if next_link:
            od.update({'next_params': next_params})
        else:
            od.update({'next_params': None})

        od.update({'previous': previous_link,})
        if previous_link:
            od.update({'previous_params': previous_params})
        else:
            od.update({'previous_params': None})

        od.update({'results': data})
        
        return Response(od)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    pagination_class = OrderLimitOffsetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        '=id', 'email', 
        'shipping_address__name', 'shipping_address__city',
    ]

    def get_queryset(self):
        '''
        Checks for filters specific fields available:
        - status (integer)
            - Is the status code of the available statuses, e.g. "Awaiting dispatch" is code 1
        '''
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status is not None:
            queryset = queryset.filter(status=status)
        
        return queryset

    @action(detail=True, methods=['post'])
    def refund_order(self, request, pk):
        """Refund the order specified by the pk
        """
        order = Order.objects.get(id=pk)
        order = order.refund()
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=['post'])
    def fulfill_order(self, request, pk):
        """Mark the order specified by pk as fulfilled
        """
        order = Order.objects.get(id=pk)
        order = order.fulfill()
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=['post'])
    def unfulfill_order(self, request, pk):
        """Unmark the order specified by pk as fulfilled
        """
        order = Order.objects.get(id=pk)
        order = order.unfulfill()
        return Response(self.get_serializer(order).data)

    @action(detail=False, methods=['get'])
    def order_statuses(self, request):
        return Response({value: text for value, text in Order.ORDER_STATUSES}, status=200)

    @action(detail=False, methods=['post'])
    def set_order_status(self, request, pk, status_code):
        order = Order.objects.get(id=pk)
        order.set_status(status_code)
        return Response(self.get_serializer(order).data)

    @action(detail=False, methods=['get'])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
