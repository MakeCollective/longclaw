from django.apps import apps
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View, TemplateView

from longclaw.basket.utils import basket_id, get_basket_items, add_to_basket, basket_total
from longclaw.basket.models import BasketItem
from longclaw.configuration.models import Configuration
from longclaw.subscriptions.models import Subscription
from longclaw.subscriptions.utils import create_subscription_order
from longclaw.orders.models import Order
from longclaw.shipping.forms import AddressForm

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

        # Get current address(es) from account details
        account = request.user.account
        shipping_address = account.shipping_address
        billing_address = account.billing_address
        
        # Get address form(s)
        shipping_address_form = AddressForm(prefix='shipping_address', instance=shipping_address)
        billing_address_form = AddressForm(prefix='billing_address', instance=billing_address)


        context.update({
            'basket': basket,
            'basket_total': basket_total(bid),
            'shipping_address_form': shipping_address_form,
            'billing_address_form': billing_address_form,
            'shipping_address': shipping_address,
            'billing_address': billing_address,
            'default_addresses': True,
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





        # Create the order based on the current basket
        # Order.objects.create()
        # create_subscription_order
        

        context.update({
            'basket': basket,
            'basket_total': basket_total(bid),
        })

        return render(request, self.template_name, context=context)


