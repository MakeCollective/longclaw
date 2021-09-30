from django.http import JsonResponse

from longclaw.subscriptions.models import Subscription

import json


def subscription_pause(request, subscription_id):
    try:
        user = request.user
    except Exception as e:
        return JsonResponse({
            'success': False
        })
    
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return JsonResponse({
            'success': False,
        })
    
    body = json.loads(request.body)
    pause_date = body.get('pause_date')

    if not pause_date:
        return JsonResponse({'success': False, 'reason': 'No pause_date parameter received'})
    
    # Check if account owns subscription or has high enough access
    account = user.account
    if subscription.account == account or user.is_superuser:
        subscription.pause(pause_date)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
    
    
def subscription_delete(request, subscription_id):
    try:
        user = request.user
    except Exception as e:
        return JsonResponse({
            'success': False
        })
    
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return JsonResponse({
            'success': False,
        })
    
    # Check if account owns subscription or has high enough access
    account = user.account
    if subscription.account == account or user.is_superuser:
        subscription.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
    

def subscription_activate(request, subscription_id):
    try:
        user = request.user
    except Exception as e:
        return JsonResponse({
            'success': False
        })
    
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return JsonResponse({
            'success': False,
        })
    
    # Check if account owns subscription or has high enough access
    account = user.account
    if subscription.account == account or user.is_superuser:
        subscription.activate()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
    
