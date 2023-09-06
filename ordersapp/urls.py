from django.urls import path
from ordersapp import views

urlpatterns = [

    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
]