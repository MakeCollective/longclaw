from django.apps import apps
from django.http import JsonResponse
from django.conf import settings
from longclaw.basket.utils import basket_id, add_to_basket
ProductVariant = apps.get_model(*settings.PRODUCT_VARIANT_MODEL.split('.'))


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