from django import template
from user_actions.models import UserAction
from wallet.models import CryptoWallet

register = template.Library()

@register.simple_tag
def get_pending_user_actions(user):
    """Returns pending user actions for the given user."""
    if not user.is_authenticated:
        return UserAction.objects.none()
    return UserAction.objects.filter(user=user, status='pending').order_by('-created_at')

@register.simple_tag
def get_usdt_wallet(user):
    """Returns the user's USDT wallet, if it exists."""
    if not user.is_authenticated:
        return None
    return user.crypto_wallets.filter(crypto_type='USDT').first()