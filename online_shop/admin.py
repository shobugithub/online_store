from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, Category, Product, Cart, CartItem, Message

# Register your models here.

# admin.site.register(User)

# @admin.register(UserAccount)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('first_name', 'email', 'is_staff', 'is_active')

admin.site.register(UserAccount)
admin.site.register(Product)    
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(Message)