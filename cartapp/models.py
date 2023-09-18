from django.db import models
from userapp.models import Product, User
from django.utils import timezone

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_added = models.DateField(auto_now_add=True)
    coupon = models.ForeignKey('cartapp.Coupons', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name
    
    def discount_amount(self):
        if self.cart and self.cart.coupon:
            discount = (self.product.price * self.quantity * self.cart.coupon.discount) / 100
            return discount
        else:
            discount = 0
            return discount

        
    def total_after_discount(self):
        sub_total = self.sub_total()
        discount = self.discount_amount()
        if discount is not None:
            return sub_total - discount
        else:
            return sub_total


class Coupons(models.Model):
    coupon_code = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    minimum_amount = models.IntegerField(default=10000)
    discount = models.IntegerField(default=0)
    is_expired = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.coupon_code
    

    def is_valid(self):
        now = timezone.now()
        if self.valid_to != now:
            self.is_expired = True
            return self.is_expired
        else:
            return self.is_expired


class UserCoupons(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=True)

    def __str__(self):
        return self.coupon.coupon_code
