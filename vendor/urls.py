from django.urls import include, path
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path('',AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    # Category CRUD
    path('category/category/add', views.add_category, name='add_category'),
    path('category/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('category/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # FoodItems CRUD
    path('category/food/add', views.add_food, name='add_food'),
    path('category/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('category/food/delete/<int:pk>/', views.delete_food, name='delete_food'),
    
]
