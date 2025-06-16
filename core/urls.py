from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, ProductViewSet, 
                    OrderViewSet, RegisterView,
                    CreateOrderView, CartViewSet, 
                    UserProfileView, ProductReviewViewSet
                    , FavoriteViewSet) 
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import update_order_status
router = DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'favorites', FavoriteViewSet, basename='favorites')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', obtain_auth_token, name='auth_login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('order/create/', CreateOrderView.as_view(), name='create_order'), 
    path('order/<int:pk>/status/', update_order_status, name='update_order_status'),
    
]