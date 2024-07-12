from django.urls import path
from store import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<slug:slug>', views.product_detail, name='product_detail'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('introduction/', views.introduction, name='introduction'),
    path('contact/', views.contact, name='contact'),
    path('verify_order/<uuid:token>/', views.verify_order, name='verify_order'),
    path('account/<str:id>/', views.account_page, name='account'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='store/password_reset.html',
        email_template_name="store/password_reset_email.html",
        success_url=reverse_lazy('store:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='store/password_reset_done.html'
    ), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='store/password_reset_confirm.html',
        success_url=reverse_lazy('store:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='store/password_reset_complete.html'
    ), name='password_reset_complete'),
]