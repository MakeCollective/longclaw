from django import forms

from longclaw.subscriptions.models import Subscription

class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = ['dispatch_frequency', 'dispatch_day_of_week', 'one_click_reminder', 'selected_payment_method']
