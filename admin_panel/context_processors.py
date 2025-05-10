from .utils import get_system_settings
from django.contrib.auth import get_user_model
from transactions.models import Transaction
from accounts.models import KYC
from dashboard.models import Investment
from django.db.models import Sum
import datetime

User = get_user_model()

def admin_stats(request):
    """
    Context processor to add common admin stats to all templates.
    This ensures variables like pending_withdrawals are available in all templates.
    """
    # Only add these variables for authenticated admin users
    if not request.user.is_authenticated or not request.user.is_staff:
        # Return minimal context for non-admin users
        return {
            'current_year': datetime.datetime.now().year,
        }
    
    # Get counts for dashboard
    total_users = User.objects.filter(is_staff=False).count()
    pending_users = User.objects.filter(is_staff=False, profile__is_approved=False).count()
    pending_deposits = Transaction.objects.filter(transaction_type='deposit', status='pending').count()
    pending_withdrawals = Transaction.objects.filter(transaction_type='withdrawal', status='pending').count()
    pending_kyc = KYC.objects.filter(status='pending').count()
    
    # Get total deposits and withdrawals
    total_deposits = Transaction.objects.filter(transaction_type='deposit', status='completed').aggregate(
        Sum('amount'))['amount__sum'] or 0
    total_withdrawals = Transaction.objects.filter(transaction_type='withdrawal', status='completed').aggregate(
        Sum('amount'))['amount__sum'] or 0
    
    # Get active investments
    active_investments = Investment.objects.filter(status='active').count()
    total_invested = Investment.objects.filter(status='active').aggregate(
        Sum('amount'))['amount__sum'] or 0
    
    return {
        'total_users': total_users,
        'pending_users': pending_users,
        'pending_deposits': pending_deposits,
        'pending_withdrawals': pending_withdrawals,
        'pending_kyc': pending_kyc,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'active_investments': active_investments,
        'total_invested': total_invested,
        'current_year': datetime.datetime.now().year,
    }


def system_settings(request):
    """
    Context processor to make system settings available in all templates.
    
    Add this to your TEMPLATES context_processors in settings.py:
    'admin_panel.context_processors.system_settings',
    """
    return {
        'system_settings': get_system_settings()
    }