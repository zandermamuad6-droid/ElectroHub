
from django.urls import path
from .views import product_list, create_product, seller_register, seller_login

urlpatterns = [
    path('', product_list, name='product-list'),
    path('create/', create_product, name='create-product'),
    path('register/', seller_register, name='seller-register'),
    path('login/', seller_login, name='seller-login'),
]
