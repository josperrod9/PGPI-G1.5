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
    path('', views.products_selected, name='home'),
    path('all-products/', views.products, name='products'),
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
    path('politica/' ,views.politica,name='politica'),
    path('opinions/' ,views.opinions,name='opinions'),
    path('send/', views.Send.as_view(), name='send'),
    path('opinions/<int:opinion_id>/', views.opinions_details,name="opinionDetails"),
    path('opinions/create/', views.create_opinion,name="opinionCreate"),
    path('opinions/<int:opinion_id>/addResponse/', views.createResponse,name="responseCreate"),
    path('orders/' ,views.getOrderByRefCode ,name='ordersByRefCode'),

]
