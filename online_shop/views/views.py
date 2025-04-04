from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Product, CartItem, Category, Cart
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from ..forms import ProductForm
from django.db.models import Q
from config import settings
import json

User = get_user_model()

# Create your views here.

class CustomRangeForPagination:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        page_obj = context['page_obj']
        left_index = page_obj.number - 1
        right_index = page_obj.number + 1

        if left_index < 1:
            left_index = 1

        if right_index > page_obj.paginator.num_pages:
            right_index = page_obj.paginator.num_pages

        custom_range = range(left_index, right_index + 1)
        context['custom_range'] = custom_range
        return context

class ProductListView(CustomRangeForPagination, ListView):
    model = Product
    template_name = 'online_store/index.html'
    context_object_name = 'products'
    ordering = ['id']
    paginate_by = 3

    def get_queryset(self):
        queryset = Product.objects.filter(is_deleted=False)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains = search_query) | Q(description__icontains = search_query)
            )
        return queryset

def edit_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('online_store:index_page')
    else:
        form = ProductForm(instance=product)

    return render(request, 'online_store/edit-product.html', {'form': form, 'product': product})

def confirm_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, 'online_store/confirm-delete.html', {'product': product})

def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.method == 'POST':
        product.is_deleted = True
        product.save()
        return redirect('online_store:index_page')
    return redirect('online_store/index.html', {'product': product})

def product_detail(request, pk, slug):
    product = get_object_or_404(Product, pk=pk, slug=slug)
    context = {
        'product': product
    }
    return render(request, 'online_store/single-product.html', context)

class CategoryListView(CustomRangeForPagination, ListView):
    model = Category
    template_name = 'online_store/categories.html'
    context_object_name = 'categories'
    ordering = ['id']
    paginate_by = 3

    def get_queryset(self):
        queryset = Category.objects.all()

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains = search_query) | Q(description__icontains = search_query)
            )
        return queryset
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        for category in context['categories']:
            category.product_list = Product.objects.filter(is_deleted=False, category=category)
        return context

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'online_store/category-detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        category = context['category']
        context['products'] = Product.objects.filter(is_deleted=False, category=category)
        return context

def get_cart(request):
    """Foydalanuvchining savatini yoki mehmon (guest) savatini qaytaradi"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_page(request):
    """Savat sahifasini ko'rsatish"""
    cart = get_cart(request)
    total_price = cart.total_cost()
    shipping = 5 if cart.items.exists() else 0  # Agar savat bo'sh bo'lmasa, yetkazib berish narxi 5$
    total_amount = total_price + shipping

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'total_price': total_price,
        'shipping': shipping,
        'total_amount': total_amount,
        'shipping_start': "2-3 days",
        'shipping_end': "5-7 days",
    }
    return render(request, "online_store/cart.html", context)

def add_to_cart(request, product_id):
    """Mahsulotni savatga qo'shish"""
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, create = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id).first()
        if not cart:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id # yengi cartni session da saqlash
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("online_store:cart_page")

def update_quantity(request, item_id):
    """Mahsulot miqdorini o'zgartirish"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart=get_cart(request))
    action = request.GET.get("action")

    if action == "add":
        cart_item.quantity += 1
    elif action == "subtract" and cart_item.quantity > 1:
        cart_item.quantity -= 1

    cart_item.save()
    return redirect("online_store:cart_page")

def remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart=get_cart(request))
    cart_item.delete()
    return redirect("online_store:cart_page")

def add_multiple_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_ids = data.get("product_ids", [])

            for product_id in product_ids:
                product = Product.objects.get(id=product_id)
                # 🟢 Savatchaga qo‘shish (Cart modeliga moslashtiring)
                Cart.objects.create(user=request.user, product=product, quantity=1)

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def go_to_checkout(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            try:
                cart = Cart.objects.get(user=user)  # Ensure cart exists
                cart_items = cart.items.all()  # Get items
            except Cart.DoesNotExist:
                return redirect("online_store:cart_page")  # If no cart, redirect

            if not cart_items.exists():
                return redirect("online_store:cart_page")  # If cart is empty, redirect

            # Calculate order details
            product_details = []
            total_price = 0
            for item in cart_items:
                subtotal = item.product.current_price * item.quantity
                total_price += subtotal
                product_details.append(f"{item.product.title} x {item.quantity} - ${subtotal:,}")

            shipping_fee = 5  # Flat shipping cost
            grand_total = total_price + shipping_fee

            # Email content
            product_list_text = "\n".join(product_details)
            subject = "Your Order Confirmation"
            body = f"""
                Dear {user.first_name},

                Your order has been successfully placed!

                Order Details:
                {product_list_text}

                Shipping: ${shipping_fee}
                Total (including VAT): ${grand_total:,}

                Expected Delivery: 2-3 days (local) or 5-7 days (international).

                Thank you for shopping with us!
            """

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            # ✅ Pass data to `checkout_success.html`
            context = {
                "product_names": ", ".join([f"{item.product.title} x {item.quantity}" for item in cart_items]),
                "total_price": total_price,
                "grand_total": grand_total,
            }
            return render(request, "online_store/checkout_success.html", context)

    return redirect("online_store:cart_page")
