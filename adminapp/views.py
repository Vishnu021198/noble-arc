from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from userapp.models import Product, Category, User, ProductImage
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from ordersapp.models import Order, OrderProduct, Payment
from cartapp.models import Coupons
from datetime import timedelta, datetime
from django.db.models import Count, Sum
from decimal import Decimal


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, email=email, password=password)
        
            if user is not None and user.is_active and user.is_superadmin:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Please provide both email and password")
        
        return redirect('index')
         
    return render(request, 'adminapp/index.html')
         


@login_required
def dashboard(request):
    if request.user.is_superadmin:
        if not request.user.is_superadmin:
            return redirect('index')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        recent_orders = Order.objects.filter(is_ordered=True).order_by('-created_at')[:10]

        last_year = end_date - timedelta(days=365)
        yearly_order_counts = (
            Order.objects
            .filter(created_at__range=(last_year, end_date), is_ordered=True)
            .values('created_at__year')
            .annotate(order_count=Count('id'))
            .order_by('created_at__year')
        )

        month = end_date - timedelta(days=30)
        monthly_earnings = (
            Order.objects
            .filter(created_at__range=(month, end_date), is_ordered=True)
            .aggregate(total_order_total=Sum('order_total'))
        )['total_order_total']

        monthly_earnings = Decimal(monthly_earnings).quantize(Decimal('0.00'))

        daily_order_counts = (
            Order.objects
            .filter(created_at__range=(start_date, end_date), is_ordered=True)
            .values('created_at__date')
            .annotate(order_count=Count('id'))
            .order_by('created_at__date')
        )

        dates = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in daily_order_counts]
        counts = [entry['order_count'] for entry in daily_order_counts]

        context = {
            'admin_name': request.user.name,
            'dates': dates,
            'counts': counts,
            'orders': recent_orders,
            'yearly_order_counts': yearly_order_counts,
            'monthly_earnings': monthly_earnings,
            'order_count': len(recent_orders),
        }

        return render(request, 'adminapp/dashboard.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")





@never_cache
@login_required
def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')




@login_required
def admin_products(request):
    if request.user.is_superadmin:
        products = Product.objects.select_related('category').all().order_by('id')
        context = {'products': products}
        return render(request, 'adminapp/admin_products.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")





@login_required
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_images = request.FILES.getlist('product_images') 
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')


        if not (product_name and category_id and price and quantity):
            messages.error(request, "Please provide all required fields.")
            return redirect('add_product')
        

        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Price and quantity must be positive numbers.")
            return redirect('add_product')
        
        if Product.objects.filter(product_name=product_name).exists():
            messages.error(request, f"A product with the name '{product_name}' already exists.")
            return redirect('add_product')
        
        category = Category.objects.get(pk=category_id)
        
        product = Product(
            product_name=product_name,
            category=category,
            description=description,
            price=price,
            quantity=quantity,
            is_available=True
        )
        product.save()
        
        for image in product_images:
            ProductImage.objects.create(product=product, image=image)
        
        return redirect('admin_products')
    
    categories = Category.objects.all().order_by('id')
    context = {'categories': categories}
    return render(request, 'adminapp/add_product.html', context)




@login_required
def edit_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')
    categories = Category.objects.all().order_by('id')

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')

        if not (product.product_name and category_id and price and quantity):
            messages.error(request, "Please provide all required fields.")
            return redirect('edit_product', product_id=product_id)

        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Price and quantity must be positive numbers.")
            return redirect('edit_product', product_id=product_id)

        if Product.objects.filter(product_name=product.product_name).exclude(pk=product_id).exists():
            messages.error(request, f"A product with the name '{product.product_name}' already exists.")
            return redirect('edit_product', product_id=product_id)

        category = Category.objects.get(pk=category_id)

        product.category = category
        product.description = description
        product.price = price
        product.quantity = quantity
        product.save()

        images = request.FILES.getlist('product_images')
        if images:
            product.images.all().delete()

            for image in images:
                ProductImage.objects.create(product=product, image=image)

        return redirect('admin_products')

    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'adminapp/edit_product.html', context)





@login_required
def soft_delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')
    product.soft_deleted = True
    product.is_available = False
    product.save()
    return redirect('admin_products')

@login_required
def undo_soft_delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')
    product.soft_deleted = False
    product.is_available = True
    product.save()
    return redirect('admin_products')





@login_required
def admin_category(request):
    categories = Category.objects.all().order_by('id')  
    context = {'categories': categories}
    return render(request, 'adminapp/admin_category.html', context)



@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if not category_name:
            messages.error(request, "Please provide a category name.")
            return redirect('add_category')

        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('add_category')

        category = Category(
            category_name=category_name,
            category_images=category_image
        )
        category.save()

        return redirect('admin_category')

    return render(request, 'adminapp/add_category.html')

@login_required
def edit_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if not category_name:
            messages.error(request, "Please provide a category name.")
            return redirect('edit_category', category_id=category_id)

        if Category.objects.filter(category_name=category_name).exclude(pk=category_id).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('edit_category', category_id=category_id)

        category.category_name = category_name
        if category_image:
            category.category_images = category_image
        category.save()

        return redirect('admin_category')

    context = {'category': category}
    return render(request, 'adminapp/edit_category.html', context)



@login_required
def soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = True
    category.is_available = False
    category.save()
    return redirect('admin_category')

@login_required
def undo_soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = False
    category.is_available = True
    category.save()
    return redirect('admin_category')





@login_required
def admin_users(request):
    users = User.objects.all().order_by('id')  
    context = {'users': users}
    return render(request, 'adminapp/admin_users.html', context)




def block_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('admin_users')
    user.is_active = False
    user.save()
    return redirect('admin_users')  


@login_required
def unblock_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('admin_users')
    user.is_active = True
    user.save()
    return redirect('admin_users')






@login_required
def admin_orders(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'adminapp/admin_orders.html', context)



@login_required
def update_order_status(request, order_id, new_status):
    
    order = get_object_or_404(Order, pk=order_id)
    
    if new_status == 'New':
        order.status = 'New'
    elif new_status == 'Accepted':
        order.status = 'Accepted'
    elif new_status == 'Completed':
        order.status = 'Completed'
    elif new_status == 'Cancelled':
        order.status = 'Cancelled'
    
    order.save()
    
    messages.success(request, f"Order #{order.order_number} has been updated to '{new_status}' status.")
    
    return redirect('admin_orders')




@login_required
def admin_order_details(request, order_id):
    order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    payments = Payment.objects.filter(order__id=order_id)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
        'orders': orders,
        'payments': payments,
    }

    return render(request, 'adminapp/admin_order_details.html', context)



@login_required
def admin_coupons(request):
    if request.user.is_superadmin:
        coupons = Coupons.objects.all()
        context = {'coupons': coupons}
        return render(request, 'adminapp/admin_coupons.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

@login_required
def add_coupons(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        description = request.POST.get('description')
        minimum_amount = request.POST.get('minimum_amount')
        discount = request.POST.get('discount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')

        try:
            minimum_amount = int(minimum_amount)
            discount = int(discount)
        except ValueError:
            messages.error(request, "Minimum Amount and Discount must be integers.")
            return redirect('add_coupons')

        coupon = Coupons(
            coupon_code=coupon_code,
            description=description,
            minimum_amount=minimum_amount,
            discount=discount,
            valid_from=valid_from,
            valid_to=valid_to
        )
        coupon.save()
        messages.success(request, "Coupon added successfully.")
        return redirect('admin_coupons')

    return render(request, 'adminapp/add_coupons.html')




@login_required
def edit_coupons(request, coupon_id):
    try:
        coupon = Coupons.objects.get(pk=coupon_id)
    except Coupons.DoesNotExist:
        return redirect('admin_coupons')

    if request.method == 'POST':
        coupon.coupon_code = request.POST.get('coupon_code')
        coupon.description = request.POST.get('description')
        coupon.minimum_amount = int(request.POST.get('minimum_amount'))
        coupon.discount = int(request.POST.get('discount'))
        coupon.valid_from = request.POST.get('valid_from')
        coupon.valid_to = request.POST.get('valid_to')
        
        coupon.save()
        
        return redirect('admin_coupons')

    context = {'coupon': coupon}
    return render(request, 'adminapp/edit_coupons.html', context)




@login_required
def delete_coupons(request, coupon_id):
    try:
        coupon = Coupons.objects.get(pk=coupon_id)
    except Coupons.DoesNotExist:
        return redirect('admin_coupons')

    if request.method == 'POST':
        coupon.delete()
        messages.success(request, "Coupon deleted successfully.")
    
    return redirect('admin_coupons')
