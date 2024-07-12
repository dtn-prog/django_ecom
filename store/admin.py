from django.contrib import admin
from store.models import *
from django.contrib.auth.admin import UserAdmin
from store.forms import CustomerUserCreationForm
from django.contrib.auth.forms import UserChangeForm

# Register your models here.

class CustomerUserAdmin(UserAdmin):
    add_form = CustomerUserCreationForm
    form = UserChangeForm
    model = CustomerUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('phone',)}),
    ) + UserAdmin.fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )
    
    
admin.site.register(CustomerUser, CustomerUserAdmin)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(ProductImage)
admin.site.register(Contact)