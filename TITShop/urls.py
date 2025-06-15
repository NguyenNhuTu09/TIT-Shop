from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Lấy token (đăng nhập)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Làm mới token
]

# Phần này để phục vụ file media, không ảnh hưởng đến lỗi 404
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)