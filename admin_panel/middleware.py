from django.shortcuts import render
from django.urls import reverse
from .models import SystemSettings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is enabled
        try:
            settings = SystemSettings.get_settings()
            maintenance_mode = settings.maintenance_mode
            maintenance_message = settings.maintenance_message
        except:
            maintenance_mode = False
            maintenance_message = "We are currently performing maintenance. Please check back later."
        
        # Skip maintenance mode for admin users and admin panel URLs
        if maintenance_mode and not request.user.is_staff and not request.user.is_superuser:
            # Allow login page
            if request.path != reverse('login') and not request.path.startswith('/admin/'):
                return render(request, 'maintenance.html', {
                    'message': maintenance_message
                })
        
        response = self.get_response(request)
        return response