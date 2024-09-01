from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_details, name='vendor_details'),

    # ADD to cart path configuration
    path('add_to_card/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # DELETE from cart
    path('decrease_cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),
]
