from django.urls import path
from online_shop.views.views import update_quantity, remove_item, add_multiple_to_cart, ProductListView, product_detail, CategoryListView, add_to_cart, cart_page, CategoryDetailView
from online_shop.views import views
from online_shop.views.auth import (account, LoginPage, CustomLogoutView, RegisterPage, update_account, ForgotPasswordPage, activate_account, ActivateEmailView, reset_password, CustomResetPasswordConfirmView,forgot_password)


app_name = 'online_store'

urlpatterns = [
    path('', ProductListView.as_view(), name='index_page'),
    
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:pk>/confirm-delete/', views.confirm_delete, name='confirm_delete_product'),
    
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='categories_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('product/<int:pk>/<slug:slug>/', product_detail, name='product_detail'),

    # path('add-to-cart/<int:product_id>/', cart_view, name='add_to_cart'),
    path('account/', account, name='account'),

    path('cart/', cart_page, name='cart_page'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', update_quantity, name='update_quantity'),
    path('cart/remove/<int:item_id>/', remove_item, name='remove_item'),
    path("add-multiple-to-cart/", add_multiple_to_cart, name="add_multiple_to_cart"),
    path('checkout/', views.go_to_checkout, name='checkout'),

    # auth 
    path('registration/', RegisterPage.as_view(), name="registration"),
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout_page'),
    path('update_account/', update_account, name='update_account'),

    # password reset
    path('forgot-password/', ForgotPasswordPage.as_view(), name='forgot_password'),
    path('activate/<str:uid>/<str:token>', ActivateEmailView.as_view(), name='confirm_mail'),
    path('reset-password/', reset_password, name='reset_password'),

]
