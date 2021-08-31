from django.conf import settings

import stripe


def create_stripe_customer(email, name, phone):
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError('Missing setting "STRIPE_SECRET_KEY"')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    customer = stripe.Customer.create(
        email=email,
        name=name,
        phone=phone,
    )
    return customer


def create_stripe_payment_method(name, number, exp_month, exp_year, cvc):
    ''' 
    Sends a request to the Stripe API to create a PaymentMethod
    '''
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError('Missing setting "STRIPE_SECRET_KEY"')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    payment_method = stripe.PaymentMethod.create(
        type='card',
        card={
            'name': name,
            'number': number,
            'exp_month': exp_month,
            'exp_year': exp_year,
            'cvc': cvc,
        }
    )
    return payment_method


def attach_stripe_payment_method(pm_id, cust_id):
    '''
    Sends a request to the Stripe API to attach a PaymentMethod to a Customer
    '''
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError('Missing setting "STRIPE_SECRET_KEY"')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    payment_method = stripe.PaymentMethod.attach(
        pm_id,
        customer=cust_id
    )
    return payment_method