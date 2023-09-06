from django.urls import path
from ordersapp import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('cash_on_delivery/<int:order_number>/', views.cash_on_delivery, name='cash_on_delivery'),
    path('order_confirmed/', views.order_confirmed, name='order_confirmed'),
]
