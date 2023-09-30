from ordersapp.models import Order, Payment, OrderProduct, Address
from ordersapp.forms import OrderForm
from cartapp.models import Coupons, UserCoupons, Cart, CartItem
from cartapp.views import _cart_id
from userapp.models import User
from django.shortcuts import render, redirect
import datetime
from django.db import transaction
import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone


# Create your views here.



@transaction.atomic
def cash_on_delivery(request, order_number):
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        return redirect('order_confirmed')
    
    total_amount = order.order_total 
   
    payment = Payment(user=current_user, payment_method="Cash On Delivery", amount_paid=total_amount, status="Not Paid")
    payment.save()
    
   
    order.is_ordered = True
    order.payment = payment
    order.save()
    
    
    cart_items = CartItem.objects.filter(user=current_user)
    
    
    for cart_item in cart_items:
        order_product = OrderProduct(
            order=order,
            payment=payment,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.price,
            ordered=True,
        )
        order_product.save()
    
    cart_items.delete()
    
    context = {'order': order}

    return render(request, 'userapp/order_confirmed.html', context)


def payments(request, order_id):
    current_user = request.user


    coupon_code = request.session['coupon_code']
    coupon = Coupons.objects.get(coupon_code=coupon_code)

    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_list')
    
    tax = 0
    shipping = 0
    grand_total = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (18 * total) / 100
    shipping = (100 * quantity)
    grand_total = total + tax + shipping - coupon.discount
    

    try:
        order = Order.objects.get(user=current_user, is_ordered=False, id=order_id)
    except Order.DoesNotExist:
        return redirect('payments')
    
    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'tax': tax,
        'discount': coupon.discount,
        'grand_total': grand_total,
    }
    return render(request, 'userapp/payments.html', context)


@login_required(login_url='user_login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        shipping = 0
        grand_total = 0
        coupon_discount = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)


        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity


        tax = (18 * total) / 100
        shipping = (100 * quantity)
        grand_total = total + tax + shipping


    except Cart.DoesNotExist:
        pass
    except CartItem.DoesNotExist:
        pass

    address_list = Address.objects.filter(user=request.user)
    default_address = address_list.filter(is_default=True).first()
    coupons = Coupons.objects.all()
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping':shipping,
        'grand_total': grand_total,
        'address_list': address_list,
        'default_address': default_address,
        'coupons': coupons,
        'coupon_discount':coupon_discount
    }
    return render(request, 'userapp/checkout.html', context)


@login_required
def set_default_address(request, address_id):
    addr_list = Address.objects.filter(user=request.user)
    for a in addr_list:
        a.is_default = False
        a.save()
    address = Address.objects.get(id=address_id)
    address.is_default=True
    address.save()
    return redirect('checkout')

@login_required
def place_order(request, total=0, quantity=0):
    current_user = request.user
    coupons = Coupons.objects.all()


    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_list')
    
    tax = 0
    shipping = 0
    grand_total = 0
    discount = 0
    

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (18 * total) / 100
    shipping = (100 * quantity)
    grand_total = total + tax + shipping
    
    if request.method == 'POST':
        
        try:
            address = Address.objects.get(user=request.user,is_default=True)
        except:
            messages.warning(request, 'No delivery address exixts! Add a address and try again')
            return redirect('checkout')
        
        
        data = Order()
        data.user = current_user
        data.first_name = address.first_name
        data.last_name = address.last_name
        data.phone = address.phone
        data.email = address.email
        data.address_line_1 = address.address_line_1
        data.address_line_2 = address.address_line_2
        data.city = address.city
        data.pincode = address.pincode
        data.order_total = grand_total
        data.shipping = shipping
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

    

      

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'shipping': shipping,
            'discount': discount,
            'grand_total': grand_total,
            'coupons': coupons,
            
        }
        return render(request, 'userapp/payments.html', context)
    else:
        return redirect('checkout')
    

from django.core.exceptions import ObjectDoesNotExist  


def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        order_id = request.POST.get('order_id')
        request.session['coupon_code'] = coupon_code

        try:
            coupon = Coupons.objects.get(coupon_code=coupon_code)
            order = Order.objects.get(id=order_id)

            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                if order.order_total >= coupon.minimum_amount:
                    if coupon.is_used_by_user(request.user):
                        messages.warning(request, 'Coupon has already been Used')
                    else:
                        updated_total = order.order_total - float(coupon.discount)
                        order.order_total = updated_total
                        order.save()

                        used_coupons = UserCoupons(user=request.user, coupon=coupon, is_used=True)
                        used_coupons.save()

                        return redirect('payments', order_id)
                else:
                    messages.warning(request, 'Coupon is not Applicable for Order Total')
            else:
                messages.warning(request, 'Coupon is not Applicable for the current date')
        except ObjectDoesNotExist:
            messages.warning(request, 'Coupon code is Invalid')
            return redirect('checkout')
           

    return redirect('payments', order_id)


def order_confirmed(request, order_number):
    user = request.user
    order = Order.objects.get(order_number=order_number)

    context = {
        'order': order,
    }
    
    return render(request, 'userapp/order_confirmed.html',context)



@transaction.atomic
def confirm_razorpay_payment(request, order_number):
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        return redirect('order_confirmed')
    
    total_amount = order.order_total 

    payment = Payment(
        user=current_user,
        payment_method="Razorpay",
        status="Paid",
        amount_paid=total_amount,
    )
    payment.save()

    order.is_ordered = True
    order.order_number = order_number
    order.payment = payment
    order.save()

    cart_items = CartItem.objects.filter(user=current_user)
    for cart_item in cart_items:
        order_product = OrderProduct(
            order=order,
            payment=payment,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.price,
            ordered=True,
        )
        order_product.save()

    cart_items.delete()

    context = {'order': order}

    return render(request, 'userapp/order_confirmed.html', context)
