from django.contrib import admin
from ordersapp.models import Payment, Order, OrderProduct, Wallet, Address

# Register your models here.

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Wallet)
admin.site.register(Address)