from django.shortcuts import render, redirect, get_object_or_404
from cartapp.models import CartItem
from ordersapp.models import Order, Payment, OrderProduct
from ordersapp.forms import OrderForm
import datetime
from userapp.models import User
from django.db import transaction
import razorpay
from django.conf import settings
from django.contrib import messages
from cartapp.models import Coupons, UserCoupons, Cart
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
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
    return redirect('order_confirmed')


def payments(request, order_id):
    current_user = request.user
    coupon_code =   request.session['coupon_code']
    coupon = Coupons.objects.get(coupon_code=coupon_code)
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_list')
    
    tax = 0
    shipping = 0
    grand_total = 0
    discount = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (18 * total) / 100
    shipping = (100 * quantity)
    grand_total = total + tax + shipping - coupon.discount
    

    order = Order.objects.get(user=current_user, is_ordered=False, id=order_id)
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

def place_order(request, total=0, quantity=0):
    current_user = request.user
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
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.pincode = form.cleaned_data['pincode']
            data.order_note = form.cleaned_data['order_note']
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
            order_number = current_date = str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'shipping': shipping,
                'tax': tax,
                'discount': discount,
                'grand_total': grand_total,
            }
            return render(request, 'userapp/payments.html', context)
    else:
        return redirect('checkout')
    

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
                        messages.error(request, 'Coupon has already been Used')
                    else:
                        updated_total = order.order_total - float(coupon.discount)
                        order.order_total = updated_total
                        order.save()

                        used_coupons = UserCoupons(user = request.user, coupon = coupon, is_used = True)
                        used_coupons.save()

                        return redirect('payments', order_id)
                
                else:
                    messages.error(request, 'Coupon is not Applicable for Order Total')
            else:
                messages.error(request, 'Coupon is not Applicable for the current date')

        except Coupons.DoesNotExist:
            messages.error(request, 'Coupon code is Invalid')

    return redirect('payments', order_id)




def razor(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)


    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (18 * total) / 100
    shipping = (100 * quantity)
    grand_total = total + tax + shipping

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.pincode = form.cleaned_data['pincode']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.shipping = shipping
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            payment_amount_paise = int(grand_total * 100)

            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
            payment = client.order.create({
                'amount': payment_amount_paise,
                'currency': 'INR',
                'payment_capture': 1,
                'external_order_id': order_number,
            })

            return redirect(payment['short_url'])

    return redirect('checkout')



def order_confirmed(request):
    
    return render(request, 'userapp/order_confirmed.html')



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
