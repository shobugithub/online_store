from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _

# Create your models here

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class UserAccountManager(BaseUserManager):
    def create_user(self, email, first_name=None, last_name=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")
        
        email = self.normalize_email(email)

        """IntegrityError xatosi kevotganini sababi "first_name" ustuni NOT NULL constraint-ga ega, 
        lekin Google OAuth2 orqali kirishda bu maydon NULL qiymat bilan kevotti."""
        first_name = first_name or 'Unknown'
        last_name = last_name or 'User daka userde'

        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, first_name, last_name, password, **extra_fields)

class UserAccount(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('First_name'), max_length=50, null=True, blank=True, default='Unknown')
    last_name = models.CharField(_('Last_name'), max_length=50, null=True, blank=True, default='User')
    email = models.EmailField(_('Email'), unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()  # Custom manager

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} - {self.email}"

class Category(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')
    is_deleted = models.BooleanField(default=False) 
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Categories"
    

class Product(models.Model):
    
    DRAFT = 'drafted'
    PUBLISHED = 'published'

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=10)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=None)
    current_price = models.DecimalField(max_digits=10, decimal_places=3, null=False, default=None)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    is_deleted = models.BooleanField(default=False)

    objects = PublishedManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.title

    def discount_percentage(self):
        """Returns the discount percentage if there's a discount."""
        if self.old_price and self.old_price > self.current_price:
            return ((self.old_price - self.current_price) / self.old_price) * 100
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Product List"

class Cart(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart ({self.user if self.user else 'Guest'})"

    def total_cost(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.current_price * self.quantity


class Message(models.Model):
    sender = models.ForeignKey(to=UserAccount, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(to=UserAccount, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} to {self.receiver} - {self.body[:50]}'