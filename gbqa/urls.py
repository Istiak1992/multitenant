from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers, serializers, viewsets

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-doc/', include(router.urls)),
    # API Routes
    url(r'^api/', include([
        # Authentication Routes
        path('auth/', include('auth.urls')),
        # Photos Routes
        path('photos/', include('photo.urls')),
        # Users Routes
        path('users/', include('users.urls')),
        # Distributors Routes
        path('distributors/', include('distributors.urls')),
        # Inspections Routes
        path('inspections/', include('inspections.urls')),
        # Config Routes
        path('config/', include('config.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site changes
admin.site.site_header = "GBQA Admin"
admin.site.site_title = "GBQA Admin Portal"
admin.site.index_title = "Welcome to GBQA Portal"
