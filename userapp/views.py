from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product,Category,User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from . import verify
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.paginator import Paginator
from django.db.models import Q
from cartapp.models import Cart, CartItem, Coupons, Wishlist
from cartapp.views import _cart_id
import requests
from ordersapp.models import Order, OrderProduct



# Create your views here.



def index(request):

    response = HttpResponse()
    response['Cache-Control'] = 'no-store'

    categories = Category.objects.all()

    context = {
        'categories': categories,
    }

    return render(request, 'userapp/index.html', context)





def about(request):
    return render(request, 'userapp/about.html')




def product_list(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        selected_category = Category.objects.get(id=selected_category_id)
        products = Product.objects.filter(category=selected_category, is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)


    context = {
        'categories': categories,
        'products': paged_products,
    }

    return render(request, 'userapp/product_list.html', context)





def product_detail(request, category_id, product_id, selected_image=None):
    categories = Category.objects.all()

    try:
        selected_category = Category.objects.get(id=category_id)
        single_product = Product.objects.get(category=selected_category, id=product_id, is_available=True)
        product_images = single_product.images.all()
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'is_out_of_stock': single_product.quantity <= 0,
        'product_images': product_images,   
    }
    return render(request, 'userapp/product_detail.html', context)





def contact(request):
    return render(request, 'userapp/contact.html')




def user_login(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('/')
            
        else:
            messages.error(request, "Email or password is incorrect")

    return render(request, 'userapp/user_login.html')




def forgot_password(request):

    if request.method == "POST":

        return redirect("/password_otp")
    
    return render(request, 'userapp/forgot_password.html')



def password_otp(request):

    if request.method == "POST":

        return redirect("/reset_password")
    
    return render(request, 'userapp/password_otp.html')



def reset_password(request):

    if request.method == "POST":

        return redirect("/login")
    
    return render(request, 'userapp/reset_password.html')




def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        try:
            validate_email(email)
        except ValidationError:
            messages.warning(request, "Invalid email address")
            return redirect('/signup')

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return redirect('/signup')

        if User.objects.filter(name=name).exists():
            messages.warning(request, "Username is already taken")
            return redirect('/signup')

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email is already t   aken")
            return redirect('/signup')

        otp = verify.generate_otp()
        print("Generated OTP:", otp)
        verify.send_otp(mobile, otp)

        request.session["signup_user_data"] = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "password": password,
            "otp": otp,
        }

        return redirect("signup_otp")

    return render(request, 'userapp/signup.html')







def signup_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_data = request.session.get("signup_user_data")
        

        if stored_data and entered_otp == stored_data["otp"]:
            
            user = User(name=stored_data["name"], email=stored_data["email"], mobile=stored_data["mobile"])
            user.set_password(stored_data["password"])
            user.is_active = True
            user.is_staff = True
            user.save()
            
            del request.session["signup_user_data"]
            
            return redirect("user_login")
        else:
            pass

    return render(request, "userapp/signup_otp.html")


@login_required
def user_profile(request):

    return render(request, 'userapp/user_profile.html')




@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        new_name = request.POST.get('name')
        new_mobile = request.POST.get('mobile')
        new_email = request.POST.get('email')

        if User.objects.filter(name=new_name).exclude(id=user.id).exists():
            messages.error(request, 'Username is already taken')
            return redirect('edit_profile')

        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, 'Email is already taken')
            return redirect('edit_profile')

        if User.objects.filter(mobile=new_mobile).exclude(id=user.id).exists():
            messages.error(request, 'Mobile number is already taken')
            return redirect('edit_profile')

        user.name = new_name
        user.mobile = new_mobile
        user.email = new_email
        user.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('user_profile')

    return render(request, 'userapp/user_profile.html')




@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'userapp/my_orders.html', context)


@login_required
def order_details(request, order_id):
    order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
    }

    return render(request, 'userapp/order_details.html', context)


@login_required
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)

        if order.status in ["New", "Accepted"]:
            order.status = "Cancelled"
            order.save()
            messages.success(request, 'Order has been cancelled successfully.')
        else:
            messages.error(request, 'Order cannot be cancelled.')

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')

    return redirect('my_orders')




@login_required
def add_address(request):
    if request.method == 'POST':
        current_user = request.user

        order = Order()
        order.user = current_user
        order.first_name = request.POST.get('first_name')
        order.last_name = request.POST.get('last_name')
        order.email = request.POST.get('email')
        order.phone = request.POST.get('phone')
        order.address_line_1 = request.POST.get('address_line_1')
        order.address_line_2 = request.POST.get('address_line_2')
        order.city = request.POST.get('city')
        order.pincode = request.POST.get('pincode')
        order.order_note = request.POST.get('order_note')

        order.order_total = 0.0
        order.shipping = 0.0
        order.tax = 0.0

        order.save()

        messages.success(request, 'New address added successfully.')

    return render(request, 'userapp/add_address.html')


@login_required
def manage_address(request):
    current_user = request.user
    addresses = Order.objects.filter(user=current_user)
    context = {
        'addresses': addresses,
    }
    return render(request, 'userapp/manage_address.html', context)


@login_required
def edit_address(request, address_id):
    address = Order.objects.get(pk=address_id)

    if request.method == 'POST':

        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.email = request.POST.get('email')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2')
        address.city = request.POST.get('city')
        address.pincode = request.POST.get('pincode')
        address.order_note = request.POST.get('order_note')

        address.save()

        messages.success(request, 'Address updated successfully.')

        return redirect('edit_address', address_id=address.id)

    

    context = {
        'address': address,
    }
    return render(request, 'userapp/edit_address.html', context)



def delete_address(request, address_id):

    address = Order.objects.get(pk=address_id)
    address.delete()

    return redirect('manage_address')

@login_required
def my_coupons(request):
    if request.user.is_authenticated:
        coupons = Coupons.objects.all()
        context = {'coupons': coupons}
        return render(request, 'userapp/my_coupons.html', context)
    else:
        return redirect('user_login')
    


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    if not Wishlist.objects.filter(user=user, product=product).exists():
        Wishlist.objects.create(user=user, product=product)
        messages.success(request, 'Product added to wishlist.')
    else:
        messages.warning(request, 'Product is already in the wishlist.')

    return redirect('product_detail', category_id=product.category.id, product_id=product.id)



@login_required
def view_wishlist(request):
    user = request.user

    wishlist_items = Wishlist.objects.filter(user=user)
    wishlist_products = [item.product for item in wishlist_items]

    return render(request, 'userapp/wishlist.html', {'wishlist_products': wishlist_products})


@login_required
def remove_from_wishlist(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=user, product=product)
        wishlist_item.delete()
        messages.success(request, 'Product removed from wishlist.')
    except Wishlist.DoesNotExist:
        messages.warning(request, 'Product was not in your wishlist.')

    return redirect('view_wishlist')



def search(request):
    products = []
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('product_name').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))

    context = {
        'products': products,
    }
    return render(request, 'userapp/product_list.html', context)





@login_required
def user_logout(request):
    logout(request)
    return redirect('/')
