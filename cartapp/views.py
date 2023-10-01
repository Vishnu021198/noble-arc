from django.shortcuts import render,redirect
from userapp.models import Product
from cartapp.models import Cart, CartItem, Coupons, UserCoupons
from ordersapp.models import Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=current_user).first()
        if cart_item:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
                
            else:
                messages.warning(request, 'Product quantity in cart exceeds available quantity.')
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            
        messages.success(request, 'Product Added to Cart')
            
        return redirect('product_list')
    
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        if cart_item:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
            else:
                messages.warning(request, 'Product quantity in cart exceeds available quantity.')
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
        messages.success(request, 'Product Added to Cart')
        return redirect('product_list')




def remove_cart(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=request.user).first()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect('cart')


def remove_cart_item(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(product=product, cart=cart)
    
    if cart_items.exists():
        cart_item_to_delete = cart_items.first()
        cart_item_to_delete.delete()
    
    return redirect('cart')







def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        shipping = 0
        grand_total = 0
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
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping': shipping,
        'grand_total': grand_total,
    }
    return render(request, 'userapp/cart.html', context)






