from django.urls import reverse

from wagtail.admin.menu import MenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup
from wagtail.contrib.modeladmin.options import modeladmin_register

from longclaw.account.models import Account


class AccountModelAdmin(ModelAdmin):
    model = Account
    menu_label = 'Accounts'
    menu_icon = 'user'
    list_display = (
        'user', 'get_first_name', 'get_last_name',
        'get_orders_total',
    )
    # list_filter = ('is_business_customer', 'gss_delivery_region',)
    search_fields = ('user',)

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else None
    get_first_name.admin_order_field = 'user__first_name'
    get_first_name.short_description = 'First name'

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else None
    get_last_name.admin_order_field = 'user__last_name'
    get_last_name.short_description = 'Last name'

    def get_orders_total(self, obj):
        return obj.orders.all().count()
    get_orders_total.short_description = 'Orders'
    

class CustomAccountGroup(ModelAdminGroup):
    menu_label = 'Account'
    menu_icon = 'user'
    menu_order = 200
    items = (
        AccountModelAdmin,
    )

    def get_submenu_items(self):
        items = super().get_submenu_items()
        # items.append(MenuItem('Account Signup', reverse('account_signup'), classnames='icon icon-user', order=900))
        return items


modeladmin_register(CustomAccountGroup)
