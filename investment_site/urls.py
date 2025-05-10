from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the handler variables
handler404 = 'accounts.views.error_404'  # Assuming 'accounts' is your main app
handler500 = 'accounts.views.error_500'
handler403 = 'accounts.views.error_403'
handler400 = 'accounts.views.error_400'  # Optional: for bad request errors

urlpatterns = [
    # Your existing URL patterns
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
