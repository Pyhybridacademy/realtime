from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    # Your existing URL patterns
    path('admin-login/', include('admin_panel.urls')),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('wallet/', include('wallet.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('user-actions/', include('user_actions.urls')),
    path('notifications/', include('notifications.urls')),
    path('transactions/', include('transactions.urls')),
    
    # Add these for serving static and media files in production
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Keep this for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
