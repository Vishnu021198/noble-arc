from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class User_manager(BaseUserManager):
    def create_user(self, name, email, mobile, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            mobile=mobile
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, name, email, mobile, password):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            name = name,
            mobile = mobile
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

    


class User(AbstractBaseUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    mobile = models.CharField(max_length=50, unique=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','mobile']

    objects = User_manager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    




class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    category_images = models.ImageField(upload_to='photos/categories', blank=True)
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

    



class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    product_images = models.ImageField(upload_to='photos/products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='photos/product', default='default_image.jpg')

    def __str__(self):
        return f"Image of {self.product.product_name}"

