from django.shortcuts import render,redirect
from .models import Product,Category

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




def login(request):

    if request.method == "POST":

        return redirect("/")


    return render(request, 'userapp/login.html')




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

        return redirect("/signup_otp")
    
    return render(request, 'userapp/signup.html')




def signup_otp(request):

    if request.method == "POST":

        return redirect("/login")

    return render(request, 'userapp/signup_otp.html')




def cart(request):
    return render(request, 'userapp/cart.html')

