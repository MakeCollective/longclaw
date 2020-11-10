from django.forms import ModelForm, ModelChoiceField
from longclaw.configuration.models import Configuration
from longclaw.shipping.models import Address, Country

class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'line_1', 'line_2', 'city', 'postcode', 'country']

    def __init__(self, *args, **kwargs):
        site = kwargs.pop('site', None)
        super(AddressForm, self).__init__(*args, **kwargs)

        self.fields['line_1'].label = 'Building identifier (optional)'
        self.fields['line_1'].widget.attrs['placeholder'] = 'Level 2, Morningside House'

        self.fields['line_2'].label = 'Street number and Name'
        self.fields['line_2'].widget.attrs['placeholder'] = '123 Good Street'

        # Edit the country field to only contain
        # countries specified for shipping
        # all_countries = True
        # if site:
        #     settings = Configuration.for_site(site)
        #     all_countries = settings.default_shipping_enabled
        # if all_countries:
        #     queryset = Country.objects.all()
        # else:

        queryset = Country.objects.exclude(shippingrate=None)
        self.fields['country'] = ModelChoiceField(queryset, empty_label=None)

        self.fields['country'].initial = Country.objects.filter(iso='NZ').first()
        # self.fields['country'].widget.attrs['disabled'] = True

