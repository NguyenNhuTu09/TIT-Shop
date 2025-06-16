from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, ProductViewSet, 
                    OrderViewSet, RegisterView,
                    CreateOrderView, CartViewSet, 
                    UserProfileView) 
from rest_framework.authtoken.views import obtain_auth_token
router = DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('orders/create/', CreateOrderView.as_view(), name='create_order'), # URL mới
    path('login/', obtain_auth_token, name='auth_login'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]