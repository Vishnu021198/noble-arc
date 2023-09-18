from django.contrib import admin
from .models import Cart, CartItem, Coupons, UserCoupons

# Register your models here.

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupons)
admin.site.register(UserCoupons)
