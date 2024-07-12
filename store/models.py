from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# Create your models here.

class CustomerUser(AbstractUser):
    #email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(blank=True, null=True, max_length=20,unique=True , validators=[
        MaxLengthValidator(20, message='phone number must no exceed 20 characters'),
        RegexValidator(regex=r'^\d+$', message='phone number must only contain digits')
    ])
    
    def __str__(self):
        return self.username
    
    

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=False)
    regular_price = models.PositiveIntegerField(default=0)
    discount_price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-created_at',)
        
    @property
    def thumbnailURL(self):
        if self.thumbnail.url:
            return self.thumbnail.url
        else:
            return ''
        
    @property
    def price(self):
        if self.discount_price is not None:
            return self.discount_price  
        return self.regular_price
        
    @property
    def is_on_sale(self):
        if self.discount_price is not None:
            return True
        return False
        
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.discount_price is not None and self.regular_price is not None:
            if self.discount_price >= self.regular_price:
                raise ValidationError("Discount price must be less than regular price.")
    
    def save(self, *args, **kwargs):
        if self.quantity > 0:
            self.in_stock = True
        else:
            self.in_stock = False
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField()
    alternative_text = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f'{self.product.name} - image {self.id}'

class Order(models.Model):
    STATUS_CHOICE = (
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('W', 'Wating To Be Confirmed'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('R', 'Returned'),
        ('X', 'Cancelled'),)
    
    PAYMENT_METHOD_CHOICE = (
        ('CC', 'Credit Card'),
        ('COD', 'Cash On Delivery'),
    )
    
    customer_user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='P', choices=STATUS_CHOICE)
    payment_method = models.CharField(max_length=255, default='CC', choices=PAYMENT_METHOD_CHOICE)
    paid = models.BooleanField(default=False)
    verification_token = models.UUIDField(null=True, blank=True)
    verification_token_expires = models.DateTimeField(null=True, blank=True)
    
    def generate_verification_token(self):
        self.verification_token = uuid.uuid4()
        self.verification_token_expires = timezone.now() + timezone.timedelta(hours=24)
        self.save()
    
    def is_verification_token_valid(self):
        return self.verification_token_expires and timezone.now() <= self.verification_token_expires

    @property
    def total_quantity(self):
        total = 0
        for order_item in self.orderitem_set.all():
            total += order_item.quantity
        return total
    
    @property
    def total_price(self):
        total = 0
        for order_item in self.orderitem_set.all():
            total += order_item.total_price
        return total
    
    def __str__(self):
        if self.customer_user is not None:
            return f'order {self.id} of {self.customer_user.username}'
        return f'order {self.id}' 

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField(default=0)
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
    
    def __str__(self):
        return f'{self.quantity} of product {self.product.name}'
    
    
class ShippingAddress(models.Model):
    customerUser = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    tinh_thanh = models.CharField(max_length=255)
    quan_huyen = models.CharField(max_length=255)
    xa_phuong = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(blank=True, null=True, max_length=20,unique=True , validators=[
        MaxLengthValidator(20, message='phone number must no exceed 20 characters'),
        RegexValidator(regex=r'^\d+$', message='phone number must only contain digits')
    ])
    email = models.EmailField()
    message = models.TextField()
    info = models.CharField(max_length=100, blank=True, default='') #this is a honeyport field