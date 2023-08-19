from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from userapp.models import Product, Category, User, ProductImage
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden



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
         



@never_cache
@login_required
def dashboard(request):
    if request.user.is_superadmin:
        if not request.user.is_superadmin:
            return redirect('index')
        
        context = {'admin_name': request.user.name}
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
def delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
    except Category.DoesNotExist:
        pass
    return redirect('admin_category')




@login_required
def admin_users(request):
    users = User.objects.all().order_by('id')  
    context = {'users': users}
    return render(request, 'adminapp/admin_users.html', context)



@login_required
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
    return render(request, 'adminapp/admin_orders.html')



@login_required
def admin_coupons(request):
    return render(request, 'adminapp/admin_coupons.html')



@login_required
def admin_banners(request):
    return render(request, 'adminapp/admin_banners.html')
