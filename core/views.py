from rest_framework import viewsets, permissions, generics
from .models import Category, Product, Order
from .serializers import (CategorySerializer, ProductSerializer, 
                          OrderSerializer, RegisterSerializer, 
                          CreateOrderSerializer)
from rest_framework import filters 
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User


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
