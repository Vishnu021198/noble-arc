from django.shortcuts import render,redirect
from .models import Product,Category,User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from twilio.rest import Client
import random
from django.contrib.sessions.models import Session
import os
from . import verify
# Create your views here.



def index(request):

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
    else:
        products = Product.objects.filter(is_available=True)

    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'userapp/product_list.html', context)





def product_detail(request, category_id, product_id):
    categories = Category.objects.all()

    try:
        selected_category = Category.objects.get(id=category_id)
        single_product = Product.objects.get(category=selected_category, id=product_id, is_available=True)
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'is_out_of_stock': single_product.quantity <= 0,
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
        user = authenticate(request,email= email,password=password)
        if user is not None:
           login(request,user)
           return redirect("/contact")
        else:
            messages.error(request,"Email or password is incorect")

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
        # Extract user input from the form
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")


        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return redirect('/signup')

        if User.objects.filter(name=name).exists():
            messages.info(request, "Username is taken")
            return redirect('/signup')

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email is taken")
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
    
    
         
    return render(request,'userapp/signup.html')






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








def cart(request):
    return render(request, 'userapp/cart.html')

