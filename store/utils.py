import json
from store.models import *


def cookie_cart(request):
    items = []
    cart_quantity = 0
    order_total_price = 0
    
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        
    i = 0
    for key, value in cart.items():
        try:
            product = Product.objects.get(slug=key)
            cart_quantity += value['quantity']
            order_total_price += product.price
            
            item_total_price = product.price * value['quantity']
            item = {
                'id': i,
                'product': {
                    'slug': product.slug,
                    'thumbnailURL': product.thumbnailURL,
                    'price': product.price,
                    'name': product.name
                },
                'total_price': item_total_price,
                'quantity': value['quantity']
            }
            i+=1
            items.append(item)
        except:
            pass
    
    return {'items':items, 'order_total_price':order_total_price, 'cart_quantity':cart_quantity}

def get_cart_quantity_cookie(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    cart_quantity = 0
    for key, value in cart.items():
        cart_quantity += value['quantity']
        
    return cart_quantity