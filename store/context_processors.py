from store.models import *
from store.utils import *

def cart_quantity(request):
    if request.user.is_authenticated: #replace with context_processor
        order,created = Order.objects.get_or_create(customer_user=request.user, status='P')
        cart_quantity = order.total_quantity
    else:
        cart_quantity = get_cart_quantity_cookie(request)
        
    return {'cart_quantity':cart_quantity}