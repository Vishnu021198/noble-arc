from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from userapp.models import Product, Category, User
from django.views.decorators.cache import cache_control




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
         




def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('index')
    
    return render(request, 'adminapp/dashboard.html')




def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')





def admin_products(request):
    products = Product.objects.all().order_by('id')  
    context = {'products': products}
    return render(request, 'adminapp/admin_products.html', context)




def add_product(request):
    return render(request, 'adminapp/add_product.html')





def admin_category(request):
    categories = Category.objects.all().order_by('id')  
    context = {'categories': categories}
    return render(request, 'adminapp/admin_category.html', context)




def add_category(request):
    return render(request, 'adminapp/add_category.html')




def admin_users(request):
    users = User.objects.all().order_by('id')  
    context = {'users': users}
    return render(request, 'adminapp/admin_users.html', context)




def admin_orders(request):
    return render(request, 'adminapp/admin_orders.html')




def admin_coupons(request):
    return render(request, 'adminapp/admin_coupons.html')




def admin_banners(request):
    return render(request, 'adminapp/admin_banners.html')
