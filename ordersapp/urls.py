from django.urls import path
from ordersapp import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('set_default_address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('payments/<int:order_id>/', views.payments, name='payments'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('cash_on_delivery/<int:order_number>/', views.cash_on_delivery, name='cash_on_delivery'),
    path('order_confirmed/<int:order_number>/', views.order_confirmed, name='order_confirmed'),
    path('confirm_razorpay_payment/<str:order_number>/', views.confirm_razorpay_payment, name='confirm_razorpay_payment'),
    # path('razor/', views.razor, name='razor'),
]
