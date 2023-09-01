from django.urls import path
from userapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_detail/<int:category_id>/<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
    path('user_login/', views.user_login, name='user_login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password_otp/', views.password_otp, name='password_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('signup/', views.signup, name='signup'),
    path('signup_otp/', views.signup_otp, name='signup_otp'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('search/', views.search, name='search'),
]
