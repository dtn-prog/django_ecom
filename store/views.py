from django.shortcuts import render,redirect
from store.models import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Case, When, Value, IntegerField, ExpressionWrapper, F
from django.db.models import Q
from store.forms import CustomerUserCreationForm, ContactForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
import json
from store.utils import *
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    products_on_sale = Product.objects.filter(discount_price__isnull=False)[:2]
    latest_products =  Product.objects.order_by('-created_at')[:4]
    context={'products_on_sale':products_on_sale, 'latest_products':latest_products, 'title':'trang chủ'}
    return render(request, 'store/store.html', context=context)

def products(request):
    search = request.GET.get('search','')
    category_slug = request.GET.get('cat','all')
    sale = request.GET.get('sale','all')

    if category_slug == 'all':
        product_list = Product.objects.all()
    else:
        product_list = Product.objects.filter(category__slug=category_slug)
    categories = Category.objects.all()
    
    if sale == 'on_sale':
        product_list = product_list.filter(discount_price__isnull=False)
    elif sale == 'not_on_sale':
        product_list = product_list.filter(discount_price__isnull=True)
    
    if search:
        product_list = product_list.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    products = product_list.annotate(calculated_price=ExpressionWrapper(
    Case(
        When(discount_price__isnull=False, then=F('discount_price')),
        default=F('regular_price'), output_field=IntegerField()
    ),
    output_field=IntegerField()
))
    sort_option = request.GET.get('sort_by', 'default')
    if request.method == 'GET':
        match sort_option:
            case 'alpha-asc':
                products = products.order_by('name')
            case 'alpha-desc':
                products = products.order_by('-name')
            case 'price-asc':
                products = products.order_by('calculated_price')
            case 'price-desc':
                products = products.order_by('-calculated_price')
            case 'created-desc':
                products = products.order_by('-created_at')
            case 'created-asc':
                products = products.order_by('created_at')
            case _:
                pass
    
    paginator = Paginator(products, 8)
    current_page_num  = request.GET.get('page', 1) 
    paginated_products = paginator.get_page(current_page_num)
    num_pages = '1' * paginator.num_pages
    context={'categories':categories,'paginated_products':paginated_products, 
             'num_pages':num_pages, 'sort_option':sort_option, 
             'search':search, 'category_slug':category_slug, 'sale':sale, 'title':'sản phẩm'}
    return render(request, 'store/products.html', context=context)


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    product_image_set = product.productimage_set.all()
    context= {'product':product, 'title':product.name, 'product_image_set':product_image_set}
    return render(request, 'store/product_detail.html', context=context)

def register_page(request):
    if request.user.is_authenticated:
        return redirect('store:home')
	
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid(): 
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    #add cookie cart to user cart
                    cookie_data = cookie_cart(request)
                    items = cookie_data['items']
                    cart_quantity = cookie_data['cart_quantity']
                    order_total_price = cookie_data['order_total_price']
                    
                    for item in items:
                        order, order_created = Order.objects.get_or_create(customer_user=user,status='P')
                        product = Product.objects.get(slug=item['product']['slug'])
                        item_quantity = item['quantity']
                        order_item, order_item_created = OrderItem.objects.get_or_create(product=product,order=order)
                        if order_item_created:
                            order_item.quantity = item_quantity
                            order_item.save()
                        else:
                            order_item.quantity += item_quantity
                            order_item.save()
                    
                    login(request, user)
                    messages.success(request, f'User {user.username} created successfully')
                    return redirect('store:home')
            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomerUserCreationForm()
   
    context = {'form': form, 'title': 'đăng ký'}
    return render(request, 'store/register.html', context)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)
        if user is not None and user.is_active:            
            cookie_data = cookie_cart(request)
            items = cookie_data['items']
            cart_quantity = cookie_data['cart_quantity']
            order_total_price = cookie_data['order_total_price']
            
            for item in items:
                order,order_created = Order.objects.get_or_create(customer_user=user,status='P')
                product = Product.objects.get(slug=item['product']['slug'])
                item_quantity = item['quantity']
                order_item, order_item_created = OrderItem.objects.get_or_create(product=product,order=order)
                if order_item_created:
                    order_item.quantity = item_quantity
                    order_item.save()
                else:
                    order_item.quantity += item_quantity
                    order_item.save()
                
            login(request, user)
            messages.success(request, 'đã đăng nhập')
            return redirect('store:home')
        else:
            messages.info(request, "sai mật không hoặc tài khoản")
            return render(request, 'store/login.html', {})

    context = {'title':'đăng nhập'}
    return render(request, 'store/login.html', context)

def logout_page(request):
    logout(request)
    response = redirect('store:login')
    response.delete_cookie('cart')
    return response

def cart(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_user=request.user, status='P')
        items = order.orderitem_set.all()
        cart_quantity = order.total_quantity
        order_total_price = order.total_price
    else:
        cookie_data = cookie_cart(request)
        items = cookie_data['items']
        cart_quantity = cookie_data['cart_quantity']
        order_total_price = cookie_data['order_total_price']
            
    context = {'items':items, 'order_total_price':order_total_price, 
               'cart_quantity':cart_quantity, 'title':'giỏ hàng'}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_user=request.user, status='P')
        cart_quantity = order.total_quantity
        order_total_price = order.total_price
        if cart_quantity <= 0:
            return redirect('store:home')
        items = order.orderitem_set.all()
    else:
        cookie_data = cookie_cart(request)
        items = cookie_data['items']
        cart_quantity = cookie_data['cart_quantity']
        order_total_price = cookie_data['order_total_price']

    context = {'items':items, 'order_total_price':order_total_price, 
               'cart_quantity':cart_quantity, 'title':'thanh toán'}
    return render(request, 'store/checkout.html', context)

def introduction(request):
    return render(request, 'store/introduction.html', {'title':'giới thiệu'})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('info') == '': # info is a honeypot field
            contact = form.save()
            messages.success(request, 'gửi thành công')
        else:
            return HttpResponseBadRequest("Invalid request")
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'title':'giới thiệu', 'form':form})

def verify_order(request, token):
    order = get_object_or_404(Order, verification_token=token)
    if order.is_verification_token_valid:
        if order.status == 'W':
            order.status = 'C'
            order.save()
            return HttpResponse("cảm hơn bạn đã mua hàng, đơn hàng được xác nhận")
        else:
            return HttpResponse("đơn hàng đã được xác nhận")
    else:
        return HttpResponse("quý khách không xác nhận đơn hàng sau 24h")


@login_required(login_url='store:login')
def account_page(request, id):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "đổi mật khẩu thành công")
    else:
        form = PasswordChangeForm(user=request.user)
    context = {'form':form}
    return render(request, 'store/account.html', context=context)