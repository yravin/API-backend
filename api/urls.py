from django.urls import path
from . import views
urlpatterns = [
   path('product/', views.product_list, name='Product_list'),
   path('product/<int:pk>/', views.product_detail, name='product_detail'),
   path('make-order/',views.make_order, name='make-order'),
   path('today_orders/',views.today_orders, name='today_orders')
    
]


