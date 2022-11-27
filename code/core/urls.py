from django.urls import path
from core import views
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    
)

app_name = 'core'

urlpatterns = [
    path('', views.products, name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('allproducts/',views.allProducts),
    path('products/<str:category>/',views.getProductsByCategories),
    path('profile/',views.profile),
    path('deleteuser/',views.delete_user),
    path('user/orders/' ,views.user_orders ,name='orders'),
    path('user/orders/<int:order_id>/edit' ,views.update_shipping_address ,name='updateOrder'),
    path('condiciones/' ,views.condiciones,name='condiciones'),
    path('opinions/' ,views.opinions,name='opinions')
    
]
