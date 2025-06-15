from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, ProductViewSet, 
                    OrderViewSet, RegisterView,
                    CreateOrderView) # Đảm bảo đã import ViewSet

router = DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('orders/create/', CreateOrderView.as_view(), name='create_order'), # URL mới
]