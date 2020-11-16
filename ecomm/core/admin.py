from django.contrib import admin
from .models import Item,OrderItem,Order,Address,Payment,Cupon,Refund

def make_refund_accepted(modeladmin,request,queryset):
    queryset.update(refund_requseted=False, refund_granted=True)

make_refund_accepted.short_discription = 'update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = [ 
        'user',
        'order_date',
        'ordered_date',
        'ordered',
        'billing_address',
        'shipping_address',
        'payment',
        'cupon',
        'refund_requseted',
        'refund_granted',
    
    ]

    list_display_links =[
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'cupon'
    ]

    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered'
    ]



admin.site.register(Item)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(Address)
admin.site.register(Cupon)
admin.site.register(Refund)



