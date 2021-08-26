from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from longclaw.account.models import PaymentMethod


@login_required(login_url=reverse_lazy('login'))
def payment_method_set_default(request, pm_id):
    ''' Replace any old defualt Payment Method with the new one requested '''

    account = request.user.account
    try:
        payment_method = PaymentMethod.objects.get(id=pm_id)
    except PaymentMethod.DoesNotExist as e:
        return JsonResponse({'success': False, 'reason': str(e)}, status=404)
    
    # Check if the payment method belongs to the Account
    if payment_method.account != account:
        return JsonResponse({'success': False, 'reason': 'Account does not have access to that Payment Method'}, status=403)

    account.active_payment_method = payment_method
    account.save()

    return JsonResponse({'success': True})


@login_required(login_url=reverse_lazy('login'))
def payment_method_deactivate(request, pm_id):
    ''' Deactivate specific Payment Method. User must be logged in and "own" that payment method '''

    account = request.user.account
    try:
        payment_method = PaymentMethod.objects.get(id=pm_id)
    except PaymentMethod.DoesNotExist as e:
        return JsonResponse({'success': False}, status=404)
    
    # Check if the payment method belongs to the Account
    if payment_method.account != account:
        return JsonResponse({'success': False, 'reason': 'Account does not have access to that Payment Method'}, status=403)

    payment_method.deactivate()

    return JsonResponse({'success': False})
    