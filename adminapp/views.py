from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache

# Create your views here.
def index(request):
    
    if request.method == "POST":
        
        return redirect("/adminapp/dashboard/")
    
    return render(request,'adminapp/index.html')

def dashboard(request):
    return render(request,'adminapp/dashboard.html')

def admin_logout(request):
    return render(request,'adminapp/index.html')

def admin_products(request):
    return render(request,'adminapp/admin_products.html')

def add_product(request):
    return render(request, 'adminapp/add_product.html')

def admin_category(request):
    return render(request,'adminapp/admin_category.html')

def add_category(request):
    return render(request, 'adminapp/add_category.html')

def admin_users(request):
    return render(request,'adminapp/admin_users.html')

def admin_orders(request):
    return render(request,'adminapp/admin_orders.html')

def admin_coupons(request):
    return render(request,'adminapp/admin_coupons.html')

def admin_banners(request):
    return render(request,'adminapp/admin_banners.html')