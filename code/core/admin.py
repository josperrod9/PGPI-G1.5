from django.contrib import admin
from django.contrib.sites.models import Site

from .models import Item, OrderItem, Order, Payment, Address, UserProfile, Response, Opinion

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'statement',
                    'shipping_address',
                    'payment'
                
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'payment',
    ]
    list_filter = ['statement']
    search_fields = [
        'user__username',
        'ref_code'
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Address, AddressAdmin)
admin.site.register(Opinion)
admin.site.register(Response)
admin.site.unregister(Site)
