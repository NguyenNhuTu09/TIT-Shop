# core/views.py
from rest_framework import viewsets, permissions
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

# ViewSet cho Category (Chỉ đọc)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint để xem danh sách danh mục sản phẩm.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Ai cũng có thể xem

# ViewSet cho Product (Đọc và ghi cho admin, chỉ đọc cho người khác)
class ProductViewSet(viewsets.ModelViewSet):
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