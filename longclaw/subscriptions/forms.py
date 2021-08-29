from django import forms

from longclaw.subscriptions.models import Subscription

class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = ['dispatch_frequency', 'dispatch_day_of_week', 'selected_payment_method', 'shipping_rate'] # 'one_click_reminder', 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dispatch_frequency'].label = 'Dispatch frequency (in weeks)'
        self.fields['dispatch_frequency'].widget.attrs.update({'min': 1, 'max': 52})
        
        self.fields['selected_payment_method'].required = True

        self.fields['shipping_rate'].label = 'Shipping option'
        self.fields['shipping_rate'].required = True