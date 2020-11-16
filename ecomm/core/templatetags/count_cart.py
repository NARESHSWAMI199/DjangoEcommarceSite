from django import template
from core.models import Order,OrderItem
register = template.Library()

@register.filter
def cart_item_count(user):
    total= 0
    if user.is_authenticated:
        try :
            qs = Order.objects.get(user=user,ordered=False)
            # order_item = OrderItem.objects.get(user=user,ordered=False)
            # return qs[0].items.count()
            if qs:
                for order_item in qs.items.all():
                    total += order_item.quantity
                return total
        except: 
            return 0
    return 0
        
@register.filter
def cart_count(user):
    total= 0
    if user.is_authenticated:
        qs = Order.objects.filter(user=user,ordered=False)
        # order_item = OrderItem.objects.get(user=user,ordered=False)
        # return qs[0].items.count()
        if qs.exists():
            return qs[0].items.count()
        return 0
    return 0
        