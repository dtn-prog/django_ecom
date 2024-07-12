from django.urls import path
from api import views

app_name = 'api'  

urlpatterns = [
    path('update_item/', views.update_item, name='update_item'),
    path('process_order/', views.process_order, name='process_order'),
]
