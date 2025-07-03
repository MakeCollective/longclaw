from django import forms

from longclaw.subscriptions.models import Subscription


class CustomDateInput(forms.DateInput):
    input_type = 'date'


class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = [
            'dispatch_frequency', 'dispatch_day_of_week', 'shipping_rate',
            'pause_until_date'
        ] # 'one_click_reminder', 
        # widgets = {
        #     'pause_until_date': CustomDateInput(),
        # }

    pause_until_date = forms.DateField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dispatch_frequency'].label = 'Frequency'

        self.fields['shipping_rate'].label = 'Shipping option'
        self.fields['shipping_rate'].required = True
