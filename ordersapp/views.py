from django.shortcuts import render, redirect
from cartapp.models import CartItem
from ordersapp.models import Order, Payment, OrderProduct
from ordersapp.forms import OrderForm
import datetime
from userapp.models import User
from django.db import transaction

# Create your views here.



@transaction.atomic
def cash_on_delivery(request, order_number):
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        return redirect('order_confirmed')
    
   
    payment = Payment(user=current_user, payment_method="Cash On Delivery", status="Not Paid")
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
        )
        order_product.save()
    
    cart_items.delete()
    
    context = {'order': order}
    return redirect('order_confirmed')


def payments(request):
    current_user = request.user
    orders = Order.objects.filter(user=current_user)
    context = {
        'orders': orders,
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
                'grand_total': grand_total,
            }
            return render(request, 'userapp/payments.html', context)
    else:
        return redirect('checkout')
    
def order_confirmed(request):
    
    return render(request, 'userapp/order_confirmed.html')