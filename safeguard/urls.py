from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework import routers
from content.views.views import ProtectedMedia
# Api router
router = routers.DefaultRouter()

urlpatterns = [
    # Admin routes
    path('admin/', admin.site.urls),
    # Api routes
    path('api/', include('content.urls')),
    path('auth/', include('customauth.urls')),
    path('protected_media/<path:path>/',
         ProtectedMedia.as_view(), name='protected_media'),
    # path('reportes/',include('content.urls2'))
]
