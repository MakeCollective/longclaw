from decimal import Decimal
from django.utils.module_loading import import_string
from django.utils import timezone
from ipware.ip import get_real_ip
from decimal import Decimal

from longclaw.basket.utils import get_basket_items, destroy_basket
from longclaw.shipping.utils import get_shipping_cost
from longclaw.coupon.utils import discount_total
from longclaw.checkout.errors import PaymentError
from longclaw.orders.models import Order, OrderItem
from longclaw.shipping.models import Address
from longclaw.configuration.models import Configuration
from longclaw.utils import GATEWAY


def create_order(email,
                 request,
                 addresses=None,
                 shipping_address=None,
                 billing_address=None,
                 shipping_option=None,
                 discount=None,
                 capture_payment=False):
    """
    Create an order from a basket and customer infomation
    """
    basket_items, current_basket_id = get_basket_items(request)

    if not basket_items:
        raise ValueError('Basket is empty, do not complete order')
    
    if addresses:
        # Longclaw < 0.2 used 'shipping_name', longclaw > 0.2 uses a consistent
        # prefix (shipping_address_xxxx)
        try:
            shipping_name = addresses['shipping_name']
        except KeyError:
            shipping_name = addresses['shipping_address_name']

        shipping_country = addresses['shipping_address_country']
        if not shipping_country:
            shipping_country = None
        shipping_address, _ = Address.objects.get_or_create(name=shipping_name,
                                                            line_1=addresses[
                                                                'shipping_address_line1'],
                                                            city=addresses[
                                                                'shipping_address_city'],
                                                            postcode=addresses[
                                                                'shipping_address_zip'],
                                                            country=shipping_country)
        shipping_address.save()
        try:
            billing_name = addresses['billing_name']
        except KeyError:
            billing_name = addresses['billing_address_name']
        billing_country = addresses['shipping_address_country']
        if not billing_country:
            billing_country = None
        billing_address, _ = Address.objects.get_or_create(name=billing_name,
                                                           line_1=addresses[
                                                               'billing_address_line1'],
                                                           city=addresses[
                                                               'billing_address_city'],
                                                           postcode=addresses[
                                                               'billing_address_zip'],
                                                           country=billing_country)
        billing_address.save()
    else:
        shipping_country = shipping_address.country

    ip_address = get_real_ip(request)
    if shipping_country and shipping_option:
        site_settings = Configuration.for_request(request)
        shipping_rate = get_shipping_cost(
            site_settings,
            shipping_address.country.pk,
            shipping_option,
            basket_id=current_basket_id,
            destination=shipping_address,
        )['rate']
    else:
        shipping_rate = Decimal(0)

    order = Order(
        email=email,
        ip_address=ip_address,
        shipping_address=shipping_address,
        billing_address=billing_address,
        shipping_rate=shipping_rate,
    )
    if request.user.account:
        order.account = request.user.account
    order.save()

    # Create the order items & compute total
    total = 0
    for item in basket_items:
        total += item.total()
        order_item = OrderItem(
            product=item.variant,
            base_product_id=item.variant.product.id,
            product_variant_id=item.variant.id,
            product_variant_price=item.variant.price,
            product_variant_ref=item.variant.ref,
            product_variant_title=item.variant.get_product_title(),
            quantity=item.quantity,
            order=order,
        )
        order_item.save()
    
    # Set the relative discount instance (if it exists) to refer to the order
    if discount:
        # last second check that the discount code can still be used
        if not discount.coupon.depleted:
            # Adjust the total by the discount
            # total, _ = discount_total(total, discount)
            # total = Decimal(total)
            total -= discount.value

    if capture_payment:
        desc = 'Payment from {} for order id #{}'.format(email, order.id)
        try:
            transaction_id = GATEWAY.create_payment(request,
                                                    total + shipping_rate,
                                                    description=desc)
            order.payment_date = timezone.now()
            order.transaction_id = transaction_id

            # Payment has succeeded, so consume the discount code used
            if discount:
                if not discount.coupon.depleted:
                    discount.consume(order)
            
            # Once the order has been successfully taken, we can empty the basket
            destroy_basket(request)
        except PaymentError as e:
            order.status = order.FAILURE
            order.status_note = str(e)

        order.save()

    return order
