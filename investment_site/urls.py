from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Add this to your urlpatterns if you want a cleaner URL for admin login
    path('admin-login/', include('admin_panel.urls')),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('wallet/', include('wallet.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('notifications/', include('notifications.urls')),
    path('transactions/', include('transactions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)