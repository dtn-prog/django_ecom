from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from store.models import *
from store.utils import cookie_cart
from api.utils import get_username_from_email
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

@api_view(['POST'])
def update_item(request):
    if request.user.is_authenticated:
        product_slug = request.data.get('product_slug')
        action = request.data.get('action')
        quantity = int(request.data.get('quantity'))    
        
        customer_user = request.user
        product = Product.objects.get(slug=product_slug)
        order,created = Order.objects.get_or_create(customer_user=customer_user, status='P')
        
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        
        if action == 'add' or action == 'add_then_checkout':
            order_item.quantity += quantity
            order_item.save()
        elif action == 'remove':
            order_item.quantity -= quantity
            order_item.save()
        elif action == 'remove_all':
            order_item.quantity = 0
            order_item.save()
        
        deleted_item_id = -1
        if order_item.quantity <= 0:
            deleted_item_id = order_item.id
            order_item.delete()
            item_quantity = 0
            item_total_price = 0
        else:
            item_quantity = order_item.quantity
            item_total_price = order_item.total_price
        
        #order.refresh_from_db()
        
        data = {
            'success': True,
            'total_quantity': order.total_quantity,
            'item_quantity': item_quantity,
            'product_price': product.price,
            'item_total_price': item_total_price,
            'order_total_price': order.total_price,
            'deleted_item_id': deleted_item_id
        }
    else:
        pass
    
    return Response(data)


@api_view(['POST'])
def process_order(request):
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone = request.data.get('phone')
    address = request.data.get('address')
    tinh_thanh = request.data.get('tinh_thanh')
    quan_huyen = request.data.get('quan_huyen')
    xa_phuong = request.data.get('xa_phuong')
    note = request.data.get('note')
    payment_method = request.data.get('payment_method')
    
    if request.user.is_authenticated:
        customer_user = request.user
        order,created = Order.objects.get_or_create(customer_user=customer_user, status='P')
        
        order.payment_method = payment_method
        order.save()
        
        cart_total = int(request.data.get('cart_quantity'))
        total_price = int(request.data.get('total_price'))
        if cart_total != order.total_quantity or total_price != order.total_price:
            return Response({"success": False})
        
        if payment_method == 'CC':
            order.status = 'C'
            order.paid = True
        else:
            order.status = 'W'
            
        
        order.save()
        
        shipping_address,created = ShippingAddress.objects.get_or_create(
            customerUser=customer_user,
            order=order,
            address=address,
            tinh_thanh=tinh_thanh,
            quan_huyen=quan_huyen,
            xa_phuong=xa_phuong,
            note=note
        )
        
        if order.status == 'W':
            order.generate_verification_token()
            verification_url = request.build_absolute_uri(
                reverse(viewname='store:verify_order', args=[str(order.verification_token)])
            )
            
            
            #time_str = order.verification_token_expires.strftime("%Y-%m-%d %H:%M:%S")
            send_mail(
                'xác nhận đơn hàng',
                f"nhấn vào link sau để xác nhận hàng: {verification_url} \n",
                settings.EMAIL_HOST_USER,
                [customer_user.email],
                fail_silently=False,
            )
            
        
    else:
        
        username = get_username_from_email(email) #user@name.com -> user_name
        
        customer_user, user_created = CustomerUser.objects.get_or_create(
            email=email
        )
        
        if user_created:
            customer_user.first_name = first_name
            customer_user.last_name = last_name
            customer_user.username = username
            customer_user.phone = phone
            customer_user.is_active = False
            customer_user.save()
        else:
            pass
        
        if payment_method == 'CC':
            order = Order.objects.create(
                customer_user=customer_user,
                status='C',
                paid=True,payment_method=payment_method
            )
        else:
            order = Order.objects.create(
                customer_user=customer_user,
                status='W',payment_method=payment_method
            )
        
        cookie_data = cookie_cart(request)
        items = cookie_data['items']
        cart_quantity = cookie_data['cart_quantity']
        order_total_price = cookie_data['order_total_price']
        
        for item in items:
            product = Product.objects.get(slug=item['product']['slug'])
            
            order_item = OrderItem.objects.create(product=product,order=order,quantity=item['quantity'])
    
        shipping_address,created = ShippingAddress.objects.get_or_create(
            customerUser=customer_user,order=order,
            address=address,tinh_thanh=tinh_thanh,quan_huyen=quan_huyen,
            xa_phuong=xa_phuong,note=note
        )
        
        if order.status == 'W':
            order.generate_verification_token()
            verification_url = request.build_absolute_uri(
                reverse(viewname='store:verify_order', args=[str(order.verification_token)])
            )
            
            send_mail(
                'xác nhận đơn hàng',
                f"nhấn vào link sau để xác nhận hàng: {verification_url}"
                f"\nsẽ không thể xác nhân sau {order.verification_token_expires.strftime("%Y-%m-%d %H:%M:%S")}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        pass

    
    data = {'success': True}
    return Response(data)


