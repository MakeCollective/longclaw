from django.db import models


class Customer(models.Model):
    '''
    Hold details about a user. Details include at a minimum the amount of information
    to perform a transaction through Stripe
    '''
    pass


class CustomerPaymentMethod(models.Model):
    pass


class Subscription(models.Model):
    pass


class SubscriptionOrder(models.Model):
    pass


class SubscriptionOrderItem(models.Model):
    pass
