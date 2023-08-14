from django.urls import path
from adminapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_products/', views.admin_products, name='admin_products'),
    path('add_product/',views.add_product, name='add_product'),
    path('admin_category/', views.admin_category, name='admin_category'),
    path('add_category/',views.add_category, name='add_category'),
    path('admin_users/', views.admin_products, name='admin_users'),
    path('admin_orders/', views.admin_products, name='admin_orders'),
    path('admin_coupons/', views.admin_products, name='admin_coupons'),
    path('admin_banners/', views.admin_products, name='admin_banners'),
]