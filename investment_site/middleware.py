from django.shortcuts import redirect
from django.urls import reverse
from user_actions.models import UserAction
from wallet.models import CryptoWallet

class PendingActionMiddleware:
    """Middleware to enforce pending user actions"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated users or staff
        if not request.user.is_authenticated or request.user.is_staff:
            return self.get_response(request)

        # Define exempt URLs
        exempt_paths = [
            '/dashboard/',
            '/wallet/deposit/',
            '/logout/',
            '/profile/',
            '/awaiting_approval/',
            '/static/',  # Allow static files
            '/media/',   # Allow media files
            '/admin/'    # Allow admin access
        ]

        # Check if the current path is exempt
        current_path = request.path
        if any(current_path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # Check for pending user actions
        pending_actions = UserAction.objects.filter(user=request.user, status='pending').first()
        if pending_actions:
            # Get USDT wallet
            usdt_wallet = CryptoWallet.objects.filter(user=request.user, crypto_type='USDT').first()
            if usdt_wallet:
                # Redirect to deposit page for the first pending action
                deposit_url = reverse('deposit', kwargs={'wallet_id': usdt_wallet.id, 'action_id': pending_actions.id})
                return redirect(deposit_url)
            else:
                # Redirect to dashboard if no USDT wallet
                return redirect('dashboard')

        return self.get_response(request)