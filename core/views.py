from rest_framework import viewsets, permissions, generics
from .models import Category, Product, Order, Cart, CartItem
from .serializers import (CategorySerializer, ProductSerializer, 
                          OrderSerializer, RegisterSerializer, 
                          CreateOrderSerializer, CartSerializer,
                          CartItemSerializer)
from rest_framework import filters 
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint để xem danh sách danh mục sản phẩm.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Ai cũng có thể xem

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho phép xem và quản lý sản phẩm.
    Hỗ trợ lọc, tìm kiếm và sắp xếp.
    """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    # Thêm các backend cho lọc, tìm kiếm, sắp xếp
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    
    # Các trường có thể lọc theo (VD: /api/products/?category=1)
    filterset_fields = ['category']
    
    # Các trường có thể tìm kiếm (VD: /api/products/?search=laptop)
    search_fields = ['name', 'description']
    
    # Các trường có thể sắp xếp (VD: /api/products/?ordering=price hoặc /api/products/?ordering=-price)
    ordering_fields = ['price', 'created_at']

    # ... hàm get_permissions giữ nguyên
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    """
    API endpoint cho phép xem và quản lý sản phẩm.
    """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug' # Dùng slug thay cho id trong URL

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny] # Ai cũng được xem
        else:
            permission_classes = [permissions.IsAdminUser] # Chỉ admin được sửa, xóa, tạo
        return [permission() for permission in permission_classes]
    
    

# ViewSet cho Order (Chỉ người dùng đã đăng nhập và là chủ đơn hàng mới được xem)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint cho phép người dùng xem lại các đơn hàng của họ.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Chỉ trả về các đơn hàng của user đang đăng nhập.
        """
        return Order.objects.filter(user=self.request.user)
    
    
class RegisterView(generics.CreateAPIView):
    """
    API endpoint để đăng ký người dùng mới.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny] # Ai cũng có quyền truy cập để đăng ký
    serializer_class = RegisterSerializer
    
    
class CreateOrderView(generics.CreateAPIView):
    """
    API endpoint để khách hàng đã đăng nhập tạo đơn hàng mới.
    """
    serializer_class = CreateOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Tự động gán user đang đăng nhập cho đơn hàng
        serializer.save(user=self.request.user)



class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)

        if product.stock < quantity:
            raise serializers.ValidationError("Số lượng tồn kho không đủ.")

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        product.stock -= quantity
        product.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        if product.stock < quantity:
            raise serializers.ValidationError("Số lượng tồn kho không đủ.")
        cart_item.quantity = quantity
        cart_item.save()
        product.stock += cart_item.quantity - quantity  # Cập nhật lại stock
        product.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        product = cart_item.product
        product.stock += cart_item.quantity
        product.save()
        cart_item.delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)