from datetime import datetime
from django.db import models
from longclaw.settings import PRODUCT_VARIANT_MODEL
from longclaw.shipping.models import Address
# from longclaw.coupon.models import Discount
from longclaw.coupon.utils import discount_total

class Order(models.Model):
    SUBMITTED = 1
    FULFILLED = 2
    CANCELLED = 3
    REFUNDED = 4
    FAILURE = 5
    ORDER_STATUSES = ((SUBMITTED, 'Submitted'),
                      (FULFILLED, 'Fulfilled'),
                      (CANCELLED, 'Cancelled'),
                      (REFUNDED, 'Refunded'),
                      (FAILURE, 'Payment Failed'))
    payment_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ORDER_STATUSES, default=SUBMITTED)
    status_note = models.CharField(max_length=128, blank=True, null=True)

    transaction_id = models.CharField(max_length=256, blank=True, null=True)

    # contact info
    email = models.EmailField(max_length=128, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    # shipping info
    shipping_address = models.ForeignKey(
        Address, blank=True, null=True, related_name="orders_shipping_address", on_delete=models.PROTECT)

    # billing info
    billing_address = models.ForeignKey(
        Address, blank=True, null=True, related_name="orders_billing_address", on_delete=models.PROTECT)

    shipping_rate = models.DecimalField(max_digits=12,
                                        decimal_places=2,
                                        blank=True,
                                        null=True)
                                    
    receipt_email_sent = models.BooleanField(default=False)

    total_paid = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    account = models.ForeignKey('account.Account', related_name='orders', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "Order #{} - {}".format(self.id, self.email)

    @property
    def total(self):
        """Total cost of the order
        """
        total = 0
        for item in self.items.all():
            total += item.total

        return round(total, 2)
    
    @property
    def final_payment(self):
        """ The total payment received
            This includes the total price (reduced by any discount applied), plus shipping
        """
        total = self.total
        if self.shipping_rate:
            total += self.shipping_rate
        if self.discounts.first():
            total, _ = discount_total(total, self.discounts.first())
        return round(total, 2)

    @property
    def total_items(self):
        """The number of individual items on the order
        """
        return self.items.count()


    def refund(self):
        """Issue a full refund for this order
        """
        from longclaw.utils import GATEWAY
        now = datetime.strftime(datetime.now(), "%b %d %Y %H:%M:%S")
        if GATEWAY.issue_refund(self.transaction_id, self.total):
            self.status = self.REFUNDED
            self.status_note = "Refunded on {}".format(now)
        else:
            self.status_note = "Refund failed on {}".format(now)
        self.save()
        return self

    def fulfill(self):
        """Mark this order as being fulfilled
        """
        self.status = self.FULFILLED
        self.save()
        return self

    def unfulfill(self):
        """Unmark this order as being fulfilled
        """
        self.status = self.SUBMITTED
        self.save()
        return self

    def cancel(self, refund=True):
        """Cancel this order, optionally refunding it
        """
        if refund:
            self.refund()
        self.status = self.CANCELLED
        self.save()
        return self
    
    def update_shipping_status(self, new_shipping_status):
        """Update the shipping status of the Order with the one provided
        """
        self.shipping_status = new_shipping_status
        self.save()
        return self


class OrderItem(models.Model):
    '''
    A snapshot of an OrderItem model at the time of the completed (paid) order transaction
    Keep a reference to the original product variant, just in case, and for easier migration
    It is not critical to maintain this reference, but populating the initial data for
    the other fields is critical

    When creating this OrderItem, populate the snapshot fields with relevant data:
    product_variant_price = product.price
    product_variant_ref = product.ref
    product_variant_title = product.get_product.title()
    '''
    product = models.ForeignKey(PRODUCT_VARIANT_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    base_product_id = models.IntegerField()
    product_variant_id = models.IntegerField()
    product_variant_price = models.DecimalField(max_digits=12, decimal_places=2)
    product_variant_ref = models.CharField(max_length=32)
    product_variant_title = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE) # A reference to the actual order
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True) # If this is ever > 1 minute different to the date_created, something is wrong

    @property
    def total(self):
        return self.quantity * self.product_variant_price
    
    def __str__(self):
        return '{} x {}'.format(self.quantity, self.product_variant_title)

