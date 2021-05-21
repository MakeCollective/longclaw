from django.apps import apps
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View, TemplateView

from longclaw.basket.utils import basket_id, get_basket_items, add_to_basket, basket_total
from longclaw.basket.models import BasketItem
from longclaw.configuration.models import Configuration
from longclaw.subscriptions.models import Subscription
from longclaw.orders.models import Order

from django.conf import settings
ProductVariant = apps.get_model(*settings.PRODUCT_VARIANT_MODEL.split('.'))
CURRENCY_HTML_CODE = Configuration.objects.first().currency_html_code


class SubscriptionIndexView(LoginRequiredMixin, View):
    login_view = reverse_lazy('login')
    template_name = 'subscriptions/subscriptions_index.html'
    
    def get(self, request):
        account = request.user.account
        subscriptions = account.subscriptions.all()

        context = {
            'subscriptions': subscriptions,
        }

        return render(request, self.template_name, context=context)

    
class SubscriptionCreateView(LoginRequiredMixin, TemplateView):
    login_view = reverse_lazy('login')
    template_name = 'subscriptions/subscription_create.html'

    def get_context(self, request):
        product_variants = ProductVariant.objects.all()
        context = {
            'product_variants': product_variants,
            'currency_html_code': CURRENCY_HTML_CODE,
        }

        return context

    def get(self, request):
        context = self.get_context(request)
        
        basket, bid = get_basket_items(request)

        context.update({
            'basket': basket,
            'basket_total': basket_total(bid),
        })

        return render(request, self.template_name, context=context)

    def post(self, request):
        context = self.get_context(request)

        # Get the basket item IDs and their quantities
        items = [{'id': k.split('item_')[1], 'quantity': v} for k, v in request.POST.items() if k.startswith('item_')]

        # Update the basket items
        for x in items:
            basket_item = BasketItem.objects.get(id=x.get('id'))
            basket_item.quantity = x.get('quantity')
            basket_item.save()

        basket, bid = get_basket_items(request)

        context.update({
            'basket': basket,
            'basket_total': basket_total(bid),
        })

        return render(request, self.template_name, context=context)


