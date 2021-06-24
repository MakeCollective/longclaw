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

from django.http import JsonResponse

def test_add_to_basket(request):
    bid = basket_id(request)

    # get 3 random variants
    variants = []
    for i in range(3):
        variants.append(ProductVariant.objects.order_by('?').first())
    
    import random
    for variant in variants:
        add_to_basket(bid, variant, random.randint(1, 5))
    
    # basket, bid = get_basket_items(request)
    return JsonResponse({'success': True})


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
    success_url = reverse_lazy('subscription_create_success')

    def get_context(self, request):
        product_variants = ProductVariant.objects.all()
        
        # Get current address(es) from account details
        account = request.user.account
        shipping_address = account.shipping_address
        billing_address = account.billing_address

        context = {
            'product_variants': product_variants,
            'currency_html_code': Configuration.objects.first().currency_html_code,
            'shipping_address': shipping_address,
            'billing_address': billing_address,
        }

        return context

    def get(self, request):
        context = self.get_context(request)
        
        basket, bid = get_basket_items(request)
        
        # Get address form(s)
        shipping_address_form = AddressForm(prefix='shipping_address', instance=context.get('shipping_address'), use_required_attribute=False)
        billing_address_form = AddressForm(prefix='billing_address', instance=context.get('billing_address'), use_required_attribute=False)

        context.update({
            'basket': basket,
            'basket_total': basket_total(bid),
            'shipping_address_form': shipping_address_form,
            'billing_address_form': billing_address_form,
            'default_addresses': True,
            'shipping_billing_address_same': True,
        })

        return render(request, self.template_name, context=context)

    def post(self, request):
        context = self.get_context(request)
        account = request.user.account

        # Get the basket item IDs and their quantities
        items = [{'id': k.split('item_')[1], 'quantity': v} for k, v in request.POST.items() if k.startswith('item_')]

        # Update the basket items
        for x in items:
            basket_item = BasketItem.objects.get(id=x.get('id'))
            basket_item.quantity = x.get('quantity')
            basket_item.save()

        basket, bid = get_basket_items(request)

        shipping_address_form = AddressForm(prefix='shipping_address', instance=context.get('shipping_address'), use_required_attribute=False)
        billing_address_form = AddressForm(prefix='billing_address', instance=context.get('billing_address'), use_required_attribute=False)

        # Get address form(s)
        default_addresses = request.POST.get('default_addresses')
        shipping_billing_address_same = request.POST.get('shipping_billing_address_same')
        if default_addresses:
            shipping_address = account.shipping_address
            billing_address = account.billing_address

            # Create order here
            create_subscription_order(
                request, account,
                shipping_address=shipping_address, 
                billing_address=billing_address,
            )
            return redirect(self.success_url)
        else:
            shipping_address_form = AddressForm(request.POST, prefix='shipping_address', instance=context.get('shipping_address'), use_required_attribute=False)

            if not shipping_billing_address_same:
                billing_address_form = AddressForm(request.POST, prefix='billing_address', instance=context.get('billing_address'), use_required_attribute=False)
            else:
                billing_address_form = AddressForm(prefix='billing_address', use_required_attribute=False)


            errors = False
            
            if not shipping_address_form.is_valid():
                print('shipping_address_form is invalid')
                errors = True
            
            if not billing_address_form.is_valid():
                print('billing_address_form is invalid')
                errors = True

            if not errors:
                print('*'*80)
                print('no errors, do the thing')
                print('*'*80)
                if shipping_address_form.changed():
                    shipping_address = shipping_address_form.save()
                
                if not shipping_billing_address_same:
                    billing_address = billing_address_form.save()
          
        
                # Create order here
                return redirect(self.success_url)


        # Create the order based on the current basket
        # Order.objects.create()
        # create_subscription_order
        

        context.update({
            'basket': basket,
            'basket_total': basket_total(bid),
            'shipping_address_form': shipping_address_form,
            'billing_address_form': billing_address_form,
            'default_addresses': request.POST.get('default_addresses'),
            'shipping_billing_address_same': request.POST.get('shipping_billing_address_same'),
        })

        return render(request, self.template_name, context=context)



class SubscriptionCreateSuccessView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'subscriptions/subscription_create_success.html'

    
    