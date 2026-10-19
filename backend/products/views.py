
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .models import Product
from .serializers import ProductSerializer, SellerRegistrationSerializer


@api_view(['GET'])
def product_list(request):
    products = Product.objects.all().order_by('-created_at')

    data = [
        {
            "id": product.id,
            "name": product.name,
            "seller": (
                product.seller.username
                if product.seller
                else "ElectroHub Seller"
            ),
            "description": product.description,
            "price": str(product.price),
            "stock": product.stock,
            "image_url": product.image_url,
        }
        for product in products
    ]

    return Response(data)


@api_view(['POST'])
def seller_register(request):
    serializer = SellerRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response(
            {
                "message": "Seller account created successfully!",
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )



@api_view(['POST'])
@permission_classes([AllowAny])
def seller_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response({
        "message": "Login successful!",
        "username": user.username,
        "token": token.key
    })




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        product = serializer.save(seller=request.user)

        return Response(
            {
                "message": "Product created successfully!",
                "id": product.id,
                "name": product.name,
                "seller": request.user.username,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )
