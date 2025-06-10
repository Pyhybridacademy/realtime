from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from accounts.models import Profile, KYC
from transactions.models import Transaction
from dashboard.models import Investment, Balance, InvestmentPlan, Activity
from user_actions.models import AccountUpgradePlan, SignalPlan, UserAction
from user_actions.models import UserAction
from wallet.models import Bank, CryptoWallet, Card
from notifications.utils import create_notification
from datetime import datetime, timedelta
from .models import SystemSettings
from .forms import SystemSettingsForm
from decimal import Decimal
from notifications.email_utils import (
    notify_user_account_approved,
    notify_user_deposit_approved,
    notify_user_withdrawal_approved,
    notify_user_investment_completed,
    notify_user_bonus
)
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def admin_logout(request):
    """Admin logout view"""
    logout(request)
    return redirect('admin_login')



User = get_user_model()

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def is_admin(user):
    if user.is_superuser or user.is_staff:
        return True
    raise PermissionDenied("You don't have permission to access this page.")

# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff

def admin_login(request):
    """Admin login view"""
    # Redirect to dashboard if already logged in as admin
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
        
    error_message = None
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error_message = 'Invalid credentials or insufficient permissions'
    
    # Get system settings
    try:
        from .models import SystemSettings
        system_settings = SystemSettings.get_settings()
    except:
        system_settings = None
    
    context = {
        'error_message': error_message,
        'system_settings': system_settings,
    }
    
    return render(request, 'admin_panel/login.html', context)

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    """Admin profile view with password change functionality"""
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('admin_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'admin_panel/profile.html', {
        'password_form': password_form,
        'user': request.user
    })


@login_required
@user_passes_test(is_admin)
def change_password(request):
    """Admin change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'admin_panel/change_password.html', {
        'form': form
    })




@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get counts for dashboard
    total_users = User.objects.filter(is_staff=False).count()
    pending_users = User.objects.filter(is_staff=False, profile__is_approved=False).count()
    pending_deposits = Transaction.objects.filter(transaction_type='deposit', status='pending').count()
    pending_withdrawals = Transaction.objects.filter(transaction_type='withdrawal', status='pending').count()
    pending_kyc = KYC.objects.filter(status='pending').count()
    
    # Get total deposits and withdrawals
    total_deposits = Transaction.objects.filter(transaction_type='deposit', status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_withdrawals = Transaction.objects.filter(transaction_type='withdrawal', status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get active investments
    active_investments = Investment.objects.filter(status='active').count()
    total_invested = Investment.objects.filter(status='active').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.all().order_by('-created_at')[:10]
    
    # Get recent users
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    
    # Get transaction stats for the last 7 days
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    daily_transactions = []
    for i in range(7):
        day = last_week + timedelta(days=i+1)
        deposits = Transaction.objects.filter(
            transaction_type='deposit', 
            status='completed',
            created_at__date=day
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal', 
            status='completed',
            created_at__date=day
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        daily_transactions.append({
            'date': day.strftime('%d %b'),
            'deposits': float(deposits),
            'withdrawals': float(withdrawals)
        })
    
    # Get investment plans for the dashboard
    investment_plans = InvestmentPlan.objects.all()
    
    context = {
        'total_users': total_users,
        'pending_users': pending_users,
        'pending_deposits': pending_deposits,
        'pending_withdrawals': pending_withdrawals,
        'pending_kyc': pending_kyc,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'active_investments': active_investments,
        'total_invested': total_invested,
        'recent_transactions': recent_transactions,
        'recent_users': recent_users,
        'daily_transactions': daily_transactions,
        'investment_plans': investment_plans,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def pending_approvals(request):
    """View for pending user approvals"""
    pending_users = User.objects.filter(is_staff=False, profile__is_approved=False)
    
    context = {
        'pending_users': pending_users
    }
    
    return render(request, 'admin_panel/pending_approvals.html', context)

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    """Approve a user"""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    
    # Update user profile
    profile = user.profile
    profile.is_approved = True
    profile.save()
    
    # Create notification for user
    create_notification(
        user,
        'approval',
        'Account Approved',
        'Your account has been approved. You can now access all features of the platform.'
    )
    
    # Send email notification to user
    notify_user_account_approved(user)
    
    messages.success(request, f'User {user.email} has been approved.')
    return redirect('pending_approvals')

@login_required
@user_passes_test(is_admin)
def reject_user(request, user_id):
    """Reject a user"""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    
    # Create notification for user
    create_notification(
        user,
        'approval',
        'Account Rejected',
        'Your account registration has been rejected. Please contact support for more information.'
    )
    
    # Delete the user
    user.delete()
    
    messages.success(request, f'User has been rejected and deleted.')
    return redirect('pending_approvals')

@login_required
@user_passes_test(is_admin)
def pending_deposits(request):
    """View for pending and approved deposits"""
    active_tab = request.GET.get('tab', 'pending')
    
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if active_tab == 'approved':
        deposits = Transaction.objects.filter(
            transaction_type='deposit', 
            status='completed'
        ).order_by('-created_at')
    else:
        deposits = Transaction.objects.filter(
            transaction_type='deposit', 
            status='pending'
        ).order_by('-created_at')
    
    if search_query:
        deposits = deposits.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            deposits = deposits.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            deposits = deposits.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    paginator = Paginator(deposits, 20)
    page_number = request.GET.get('page')
    deposits_page = paginator.get_page(page_number)
    
    pending_count = Transaction.objects.filter(transaction_type='deposit', status='pending').count()
    approved_count = Transaction.objects.filter(transaction_type='deposit', status='completed').count()
    
    context = {
        'deposits': deposits_page,
        'active_tab': active_tab,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'search_query': search_query,
        'date_from': date_from if isinstance(date_from, str) else date_from.strftime('%Y-%m-%d') if date_from else '',
        'date_to': date_to if isinstance(date_to, str) else date_to.strftime('%Y-%m-%d') if date_to else '',
    }
    
    return render(request, 'admin_panel/pending_deposits.html', context)

@login_required
@user_passes_test(is_admin)
def approve_deposit(request, transaction_id):
    """Approve a deposit and update linked user actions"""
    transaction = get_object_or_404(Transaction, id=transaction_id, transaction_type='deposit', status='pending')
    
    # Update transaction status
    transaction.status = 'completed'
    transaction.save()
    
    # Update user's wallet balance
    try:
        wallet = CryptoWallet.objects.get(user=transaction.user, crypto_type=transaction.crypto_type)
        wallet.balance += transaction.amount
        wallet.save()
    except CryptoWallet.DoesNotExist:
        wallet = CryptoWallet.objects.create(
            user=transaction.user,
            crypto_type=transaction.crypto_type,
            balance=transaction.amount,
            address=f'{transaction.crypto_type.lower()}-{transaction.user.id}-{hash(transaction.user.email)[:8]}'
        )
    
    # Update user's balance
    try:
        balance = Balance.objects.get(user=transaction.user)
        balance.total += transaction.amount
        balance.deposit += transaction.amount
        balance.save()
    except Balance.DoesNotExist:
        Balance.objects.create(
            user=transaction.user,
            total=transaction.amount,
            deposit=transaction.amount,
            profit=0,
            bonus=0
        )
    
    # Check for linked user actions
    action = UserAction.objects.filter(transaction=transaction, status='pending').first()
    if action:
        action.status = 'completed'
        action.save()
        create_notification(
            transaction.user,
            'action_deposit',
            'Action Deposit Approved',
            f'Your deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} has been approved.'
        )
        Activity.objects.create(
            user=transaction.user,
            activity_type='other',
            description=f'Deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} approved.'
        )
    
    # Create notification for user
    create_notification(
        transaction.user,
        'deposit',
        'Deposit Approved',
        f'Your deposit of {transaction.amount} {transaction.crypto_type} has been approved and added to your wallet.'
    )
    
    # Send email notification to user
    notify_user_deposit_approved(transaction)
    
    # Log activity
    Activity.objects.create(
        user=transaction.user,
        activity_type='deposit',
        description=f'Deposit of {transaction.amount} {transaction.crypto_type} has been approved.'
    )
    
    messages.success(request, f'Deposit of {transaction.amount} {transaction.crypto_type} for user {transaction.user.email} has been approved.')
    return redirect('pending_deposits')

@login_required
@user_passes_test(is_admin)
def reject_deposit(request, transaction_id):
    """Reject a deposit and update linked user actions"""
    transaction = get_object_or_404(Transaction, id=transaction_id, transaction_type='deposit', status='pending')
    
    # Update transaction status
    transaction.status = 'rejected'
    transaction.save()
    
    # Check for linked user actions
    action = UserAction.objects.filter(transaction=transaction, status='pending').first()
    if action:
        action.status = 'rejected'
        action.save()
        create_notification(
            transaction.user,
            'action_deposit',
            'Action Deposit Rejected',
            f'Your deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} has been rejected.'
        )
        Activity.objects.create(
            user=transaction.user,
            activity_type='other',
            description=f'Deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} rejected.'
        )
    
    # Create notification for user
    create_notification(
        transaction.user,
        'deposit',
        'Deposit Rejected',
        f'Your deposit of {transaction.amount} {transaction.crypto_type} has been rejected. Please contact support for more information.'
    )
    
    # Log activity
    Activity.objects.create(
        user=transaction.user,
        activity_type='deposit',
        description=f'Deposit of {transaction.amount} {transaction.crypto_type} has been rejected.'
    )
    
    messages.success(request, f'Deposit of {transaction.amount} {transaction.crypto_type} for user {transaction.user.email} has been rejected.')
    return redirect('pending_deposits')

@login_required
@user_passes_test(is_admin)
def pending_withdrawals(request):
    """View for managing both pending and approved withdrawals"""
    # Get the active tab from the request
    active_tab = request.GET.get('tab', 'pending')
    
    # Get search parameters
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base query for withdrawals based on active tab
    if active_tab == 'approved':
        withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal', 
            status='completed'
        ).order_by('-updated_at')
    else:  # Default to pending
        withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal', 
            status='pending'
        ).order_by('-created_at')
    
    # Apply search filter if provided
    if search_query:
        withdrawals = withdrawals.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(withdrawal_details__icontains=search_query)
        )
    
    # Apply date filters if provided
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            withdrawals = withdrawals.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            withdrawals = withdrawals.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    # Paginate results
    paginator = Paginator(withdrawals, 20)  # Show 20 withdrawals per page
    page_number = request.GET.get('page')
    withdrawals_page = paginator.get_page(page_number)
    
    # Count totals for both tabs
    pending_count = Transaction.objects.filter(transaction_type='withdrawal', status='pending').count()
    approved_count = Transaction.objects.filter(transaction_type='withdrawal', status='completed').count()
    
    context = {
        'withdrawals': withdrawals_page,
        'active_tab': active_tab,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'search_query': search_query,
        'date_from': date_from if isinstance(date_from, str) else date_from.strftime('%Y-%m-%d') if date_from else '',
        'date_to': date_to if isinstance(date_to, str) else date_to.strftime('%Y-%m-%d') if date_to else '',
    }
    
    return render(request, 'admin_panel/pending_withdrawals.html', context)


@login_required
@user_passes_test(is_admin)
def approve_withdrawal(request, transaction_id):
    """Approve a withdrawal"""
    transaction = get_object_or_404(Transaction, id=transaction_id, transaction_type='withdrawal', status='pending')
    
    # Update transaction status
    transaction.status = 'completed'
    transaction.save()
    
    # Update user's wallet balance
    try:
        wallet = CryptoWallet.objects.get(user=transaction.user, crypto_type=transaction.crypto_type)
        
        # Check if user has enough balance
        if wallet.balance >= transaction.amount:
            wallet.balance -= transaction.amount
            wallet.save()
            
            # Update user's balance
            try:
                balance = Balance.objects.get(user=transaction.user)
                balance.total -= transaction.amount
                balance.save()
            except Balance.DoesNotExist:
                pass
            
            # Create notification for user
            create_notification(
                transaction.user,
                'withdrawal',
                'Withdrawal Approved',
                f'Your withdrawal of {transaction.amount} {transaction.crypto_type} has been approved and processed.'
            )
            
            # Send email notification to user
            notify_user_withdrawal_approved(transaction)
            
            # Log activity
            Activity.objects.create(
                user=transaction.user,
                activity_type='withdrawal',
                description=f'Withdrawal of {transaction.amount} {transaction.crypto_type} has been approved.'
            )
            
            messages.success(request, f'Withdrawal of {transaction.amount} {transaction.crypto_type} for user {transaction.user.email} has been approved.')
        else:
            # If user doesn't have enough balance, reject the withdrawal
            transaction.status = 'rejected'
            transaction.save()
            
            # Create notification for user
            create_notification(
                transaction.user,
                'withdrawal',
                'Withdrawal Rejected',
                f'Your withdrawal of {transaction.amount} {transaction.crypto_type} has been rejected due to insufficient balance.'
            )
            
            messages.error(request, f'Withdrawal of {transaction.amount} {transaction.crypto_type} for user {transaction.user.email} has been rejected due to insufficient balance.')
    except CryptoWallet.DoesNotExist:
        # If wallet doesn't exist, reject the withdrawal
        transaction.status = 'rejected'
        transaction.save()
        
        # Create notification for user
        create_notification(
            transaction.user,
            'withdrawal',
            'Withdrawal Rejected',
            f'Your withdrawal of {transaction.amount} {transaction.crypto_type} has been rejected. Wallet not found.'
        )
        
        messages.error(request, f'Withdrawal of {transaction.amount} {transaction.crypto_type} for user {transaction.user.email} has been rejected. Wallet not found.')
    
    return redirect('pending_withdrawals')

@login_required
@user_passes_test(is_admin)
def reject_withdrawal(request, transaction_id):
    """Reject a withdrawal"""
    transaction = get_object_or_404(Transaction, id=transaction_id, transaction_type='withdrawal', status='pending')
    
    # Update transaction status
    transaction.status = 'rejected'
    transaction.save()
    
    # Create notification for user
    create_notification(
        transaction.user,
        'withdrawal',
        'Withdrawal Rejected',
        f'Your withdrawal of {transaction.amount} {transaction.crypto_type} has been rejected. Please contact support for more information.'
    )
    
    # Log activity
    Activity.objects.create(
        user=transaction.user,
        activity_type='withdrawal',
        description=f'Withdrawal of {transaction.amount} {transaction.crypto_type} has been rejected.'
    )
    
    messages.success(request, f'Withdrawal of {transaction.amount} {transaction.crypto_type} for user {transaction.user.email} has been rejected.')
    return redirect('pending_withdrawals')

@login_required
@user_passes_test(is_admin)
def investments(request):
    """View for managing investments"""
    active_investments = Investment.objects.filter(status='active')
    completed_investments = Investment.objects.filter(status='completed')
    
    context = {
        'active_investments': active_investments,
        'completed_investments': completed_investments
    }
    
    return render(request, 'admin_panel/investments.html', context)

@login_required
@user_passes_test(is_admin)
def complete_investment(request, investment_id):
    """Complete an investment and add profit to user"""
    investment = get_object_or_404(Investment, id=investment_id, status='active')
    
    # Update investment status
    investment.status = 'completed'
    investment.save()
    
    # Add profit to user's balance
    try:
        balance = Balance.objects.get(user=investment.user)
        balance.total += investment.expected_profit
        balance.profit += investment.expected_profit
        balance.save()
    except Balance.DoesNotExist:
        Balance.objects.create(
            user=investment.user,
            total=investment.expected_profit,
            deposit=0,
            profit=investment.expected_profit,
            bonus=0
        )
    
    # Create transaction record for profit
    Transaction.objects.create(
        user=investment.user,
        transaction_type='profit',
        amount=investment.expected_profit,
        currency=investment.user.profile.currency,
        status='completed'
    )
    
    # Create notification for user
    create_notification(
        investment.user,
        'investment',
        'Investment Completed',
        f'Your investment of {investment.amount} {investment.user.profile.currency} has been completed with a profit of {investment.expected_profit} {investment.user.profile.currency}.'
    )
    
    # Send email notification to user
    notify_user_investment_completed(investment)
    
    # Log activity
    Activity.objects.create(
        user=investment.user,
        activity_type='investment',
        description=f'Investment of {investment.amount} {investment.user.profile.currency} has been completed with a profit of {investment.expected_profit} {investment.user.profile.currency}.'
    )
    
    messages.success(request, f'Investment for user {investment.user.email} has been completed with a profit of {investment.expected_profit} {investment.user.profile.currency}.')
    return redirect('admin_investments')

@login_required
@user_passes_test(is_admin)
def cancel_investment(request, investment_id):
    """Cancel an investment and refund the user"""
    investment = get_object_or_404(Investment, id=investment_id, status='active')
    
    # Update investment status
    investment.status = 'cancelled'
    investment.save()
    
    # Refund the investment amount to user's balance
    try:
        balance = Balance.objects.get(user=investment.user)
        balance.total += investment.amount
        balance.save()
    except Balance.DoesNotExist:
        Balance.objects.create(
            user=investment.user,
            total=investment.amount,
            deposit=investment.amount,
            profit=0,
            bonus=0
        )
    
    # Create transaction record for refund
    Transaction.objects.create(
        user=investment.user,
        transaction_type='deposit',
        amount=investment.amount,
        currency=investment.user.profile.currency,
        status='completed'
    )
    
    # Create notification for user
    create_notification(
        investment.user,
        'investment',
        'Investment Cancelled',
        f'Your investment of {investment.amount} {investment.user.profile.currency} has been cancelled and refunded to your account.'
    )
    
    # Log activity
    Activity.objects.create(
        user=investment.user,
        activity_type='investment',
        description=f'Investment of {investment.amount} {investment.user.profile.currency} has been cancelled and refunded.'
    )
    
    messages.success(request, f'Investment for user {investment.user.email} has been cancelled and refunded.')
    return redirect('investments')

@login_required
@user_passes_test(is_admin)
def view_user(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    
    # Get user's wallets
    wallets = CryptoWallet.objects.filter(user=user)
    
    # Get user's transactions
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')
    
    # Get user's investments
    investments = Investment.objects.filter(user=user).order_by('-created_at')
    
    # Get user's KYC status
    try:
        kyc = KYC.objects.get(user=user)
        kyc_status = kyc.status
    except KYC.DoesNotExist:
        kyc_status = 'not_submitted'
    
    # Get user's balance
    try:
        balance = Balance.objects.get(user=user)
    except Balance.DoesNotExist:
        balance = None
    
    # Get user's activities
    activities = Activity.objects.filter(user=user).order_by('-timestamp')[:10]
    
    context = {
        'user': user,
        'profile': user.profile,
        'wallets': wallets,
        'transactions': transactions,
        'investments': investments,
        'kyc_status': kyc_status,
        'balance': balance,
        'activities': activities
    }
    
    return render(request, 'admin_panel/view_user.html', context)

@login_required
@user_passes_test(is_admin)
def add_bonus(request, user_id):
    """Add bonus to user"""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                messages.error(request, 'Amount must be greater than zero.')
                return redirect('view_user', user_id=user.id)
            
            # Add bonus to user's balance
            try:
                balance = Balance.objects.get(user=user)
                balance.total += amount
                balance.bonus += amount
                balance.save()
            except Balance.DoesNotExist:
                Balance.objects.create(
                    user=user,
                    total=amount,
                    deposit=0,
                    profit=0,
                    bonus=amount
                )
            
            # Create transaction record for bonus
            Transaction.objects.create(
                user=user,
                transaction_type='bonus',
                amount=amount,
                currency=user.profile.currency,
                status='completed'
            )
            
            # Create notification for user
            create_notification(
                user,
                'bonus',
                'Bonus Added',
                f'A bonus of {amount} {user.profile.currency} has been added to your account.'
            )
            
            # Send email notification to user
            notify_user_bonus(user, amount, user.profile.currency)
            
            # Log activity
            Activity.objects.create(
                user=user,
                activity_type='other',
                description=f'Bonus of {amount} {user.profile.currency} has been added to your account.'
            )
            
            messages.success(request, f'Bonus of {amount} {user.profile.currency} has been added to user {user.email}.')
        except ValueError:
            messages.error(request, 'Invalid amount.')
    
    return redirect('view_user', user_id=user.id)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """View for managing all users"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.filter(is_staff=False)
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) | 
            Q(profile__phone_number__icontains=search_query) |
            Q(profile__country__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter == 'approved':
        users = users.filter(profile__is_approved=True)
    elif status_filter == 'pending':
        users = users.filter(profile__is_approved=False)
    
    # Paginate results
    paginator = Paginator(users, 20)  # Show 20 users per page
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'status_filter': status_filter
    }
    
    return render(request, 'admin_panel/manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def pending_kyc(request):
    """View for managing KYC verifications with tabs for pending and approved"""
    active_tab = request.GET.get('tab', 'pending')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    if active_tab == 'approved':
        kyc_queryset = KYC.objects.filter(status='approved').order_by('-updated_at')
    else:  # Default to pending
        kyc_queryset = KYC.objects.filter(status='pending').order_by('-created_at')
    
    # Apply search filter if provided
    if search_query:
        kyc_queryset = kyc_queryset.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Apply date filters if provided
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        if active_tab == 'approved':
            kyc_queryset = kyc_queryset.filter(updated_at__date__gte=date_from_obj)
        else:
            kyc_queryset = kyc_queryset.filter(created_at__date__gte=date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        if active_tab == 'approved':
            kyc_queryset = kyc_queryset.filter(updated_at__date__lte=date_to_obj)
        else:
            kyc_queryset = kyc_queryset.filter(created_at__date__lte=date_to_obj)
    
    # Get counts for tabs
    pending_count = KYC.objects.filter(status='pending').count()
    approved_count = KYC.objects.filter(status='approved').count()
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(kyc_queryset, 10)  # Show 10 KYC verifications per page
    
    try:
        kyc_list = paginator.page(page)
    except PageNotAnInteger:
        kyc_list = paginator.page(1)
    except EmptyPage:
        kyc_list = paginator.page(paginator.num_pages)
    
    context = {
        'kyc_list': kyc_list,
        'active_tab': active_tab,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'pending_count': pending_count,
        'approved_count': approved_count,
    }
    
    return render(request, 'admin_panel/pending_kyc.html', context)

@login_required
@user_passes_test(is_admin)
def view_kyc(request, kyc_id):
    """View KYC details"""
    kyc = get_object_or_404(KYC, id=kyc_id)
    
    context = {
        'kyc': kyc,
        'user': kyc.user,
        'profile': kyc.user.profile
    }
    
    return render(request, 'admin_panel/view_kyc.html', context)

@login_required
@user_passes_test(is_admin)
def approve_kyc(request, kyc_id):
    """Approve a KYC verification"""
    kyc = get_object_or_404(KYC, id=kyc_id, status='pending')
    
    # Update KYC status
    kyc.status = 'approved'
    kyc.save()
    
    # Create notification for user
    create_notification(
        kyc.user,
        'kyc',
        'KYC Approved',
        'Your KYC verification has been approved.'
    )
    
    # Log activity
    Activity.objects.create(
        user=kyc.user,
        activity_type='kyc',
        description='Your KYC verification has been approved.'
    )
    
    messages.success(request, f'KYC verification for user {kyc.user.email} has been approved.')
    return redirect('pending_kyc')

@login_required
@user_passes_test(is_admin)
def reject_kyc(request, kyc_id):
    """Reject a KYC verification"""
    kyc = get_object_or_404(KYC, id=kyc_id, status='pending')
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        # Update KYC status
        kyc.status = 'rejected'
        kyc.rejection_reason = rejection_reason
        kyc.save()
        
        # Create notification for user
        create_notification(
            kyc.user,
            'kyc',
            'KYC Rejected',
            f'Your KYC verification has been rejected. Reason: {rejection_reason}'
        )
        
        # Log activity
        Activity.objects.create(
            user=kyc.user,
            activity_type='kyc',
            description=f'Your KYC verification has been rejected. Reason: {rejection_reason}'
        )
        
        messages.success(request, f'KYC verification for user {kyc.user.email} has been rejected.')
        return redirect('pending_kyc')
    
    context = {
        'kyc': kyc,
        'user': kyc.user
    }
    
    return render(request, 'admin_panel/reject_kyc.html', context)

# Fix for the investment_plans view
# Make sure to import Sum from django.db.models



@login_required
@user_passes_test(is_admin)
def investment_plans(request):
    """View for managing investment plans"""
    plans = InvestmentPlan.objects.all()
    
    # Get the system settings
    system_settings = SystemSettings.get_settings()
    
    context = {
        'plans': plans,
        'system_settings': system_settings,
    }
    
    return render(request, 'admin_panel/investment_plans.html', context)


@login_required
@user_passes_test(is_admin)
def add_investment_plan(request):
    """Add a new investment plan"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        minimum_amount = request.POST.get('minimum_amount')
        maximum_amount = request.POST.get('maximum_amount')
        return_percentage = request.POST.get('return_percentage')
        duration_days = request.POST.get('duration_days')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            # Create new investment plan
            InvestmentPlan.objects.create(
                name=name,
                description=description,
                minimum_amount=float(minimum_amount),
                maximum_amount=float(maximum_amount),
                return_percentage=float(return_percentage),
                duration_days=int(duration_days),
                is_active=is_active
            )
            
            messages.success(request, f'Investment plan "{name}" has been created successfully.')
            return redirect('admin_investment_plans') 
        except ValueError:
            messages.error(request, 'Invalid input. Please check your values.')
    
    return render(request, 'admin_panel/add_investment_plan.html')

@login_required
@user_passes_test(is_admin)
def edit_investment_plan(request, plan_id):
    """Edit an investment plan"""
    plan = get_object_or_404(InvestmentPlan, id=plan_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        minimum_amount = request.POST.get('minimum_amount')
        maximum_amount = request.POST.get('maximum_amount')
        return_percentage = request.POST.get('return_percentage')
        duration_days = request.POST.get('duration_days')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            # Update investment plan
            plan.name = name
            plan.description = description
            plan.minimum_amount = float(minimum_amount)
            plan.maximum_amount = float(maximum_amount)
            plan.return_percentage = float(return_percentage)
            plan.duration_days = int(duration_days)
            plan.is_active = is_active
            plan.save()
            
            messages.success(request, f'Investment plan "{name}" has been created successfully.')
            return redirect('admin_investment_plans') 
        except ValueError:
            messages.error(request, 'Invalid input. Please check your values.')
    
    context = {
        'plan': plan
    }
    
    return render(request, 'admin_panel/edit_investment_plan.html', context)

@login_required
@user_passes_test(is_admin)
def delete_investment_plan(request, plan_id):
    """Delete an investment plan"""
    plan = get_object_or_404(InvestmentPlan, id=plan_id)
    
    # Check if there are active investments using this plan
    active_investments = Investment.objects.filter(plan=plan, status='active').exists()
    
    if active_investments:
        messages.error(request, f'Cannot delete plan "{plan.name}" because there are active investments using it.')
        return redirect('investment_plans')
    
    plan_name = plan.name
    plan.delete()
    
    messages.success(request, f'Investment plan "{plan_name}" has been deleted successfully.')
    return redirect('admin_investment_plans')

@login_required
@user_passes_test(is_admin)
def reports(request):
    """View for generating reports"""
    report_type = request.GET.get('type', 'transactions')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Set default date range to last 30 days if not specified
    today = timezone.now().date()
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=30)
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    else:
        end_date = today
    
    # Generate report based on type
    if report_type == 'transactions':
        # Get all transactions in date range
        transactions = Transaction.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).order_by('-created_at')
        
        # Calculate totals
        deposits = transactions.filter(transaction_type='deposit', status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        withdrawals = transactions.filter(transaction_type='withdrawal', status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        profits = transactions.filter(transaction_type='profit', status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        bonuses = transactions.filter(transaction_type='bonus', status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        
        context = {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'transactions': transactions,
            'deposits': deposits,
            'withdrawals': withdrawals,
            'profits': profits,
            'bonuses': bonuses
        }
    elif report_type == 'users':
        # Get user registrations in date range
        users = User.objects.filter(
            date_joined__date__gte=start_date,
            date_joined__date__lte=end_date,
            is_staff=False
        ).order_by('-date_joined')
        
        # Calculate totals
        total_users = users.count()
        approved_users = users.filter(profile__is_approved=True).count()
        pending_users = users.filter(profile__is_approved=False).count()
        
        context = {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'users': users,
            'total_users': total_users,
            'approved_users': approved_users,
            'pending_users': pending_users
        }
    elif report_type == 'investments':
        # Get investments in date range
        investments = Investment.objects.filter(
            start_date__date__gte=start_date,
            start_date__date__lte=end_date
        ).order_by('-start_date')
        
        # Calculate totals
        total_invested = investments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_profit = investments.aggregate(Sum('expected_profit'))['expected_profit__sum'] or 0
        active_investments = investments.filter(status='active').count()
        completed_investments = investments.filter(status='completed').count()
        
        context = {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'investments': investments,
            'total_invested': total_invested,
            'total_profit': total_profit,
            'active_investments': active_investments,
            'completed_investments': completed_investments
        }
    else:
        context = {
            'report_type': 'invalid',
            'start_date': start_date,
            'end_date': end_date
        }
    
    return render(request, 'admin_panel/reports.html', context)




def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def system_settings(request):
    """View for managing system settings"""
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            
            # Update Django email settings if email settings were changed
            if any(field in form.changed_data for field in ['email_host', 'email_port', 'email_host_user', 'email_host_password', 'email_use_tls']):
                from django.conf import settings as django_settings
                from django.core.mail.backends.smtp import EmailBackend
                
                # Update Django settings
                django_settings.EMAIL_HOST = form.cleaned_data['email_host']
                django_settings.EMAIL_PORT = form.cleaned_data['email_port']
                django_settings.EMAIL_HOST_USER = form.cleaned_data['email_host_user']
                django_settings.EMAIL_HOST_PASSWORD = form.cleaned_data['email_host_password']
                django_settings.EMAIL_USE_TLS = form.cleaned_data['email_use_tls']
                django_settings.DEFAULT_FROM_EMAIL = form.cleaned_data['default_from_email']
                
                # Test email connection
                try:
                    backend = EmailBackend(
                        host=django_settings.EMAIL_HOST,
                        port=django_settings.EMAIL_PORT,
                        username=django_settings.EMAIL_HOST_USER,
                        password=django_settings.EMAIL_HOST_PASSWORD,
                        use_tls=django_settings.EMAIL_USE_TLS
                    )
                    connection = backend.open()
                    if connection:
                        backend.close()
                        messages.success(request, "Email settings updated and connection tested successfully.")
                    else:
                        messages.warning(request, "Email settings updated but connection test failed.")
                except Exception as e:
                    messages.error(request, f"Email settings updated but connection test failed: {str(e)}")
            else:
                messages.success(request, "System settings updated successfully.")
            
            return redirect('system_settings')
    else:
        form = SystemSettingsForm(instance=settings)
    
    return render(request, 'admin_panel/system_settings.html', {
        'form': form,
        'settings': settings,
    })

@login_required
@user_passes_test(is_admin)
def payment_methods(request):
    """View for managing user payment methods (cards and bank accounts)"""
    # Get the active tab from the request
    active_tab = request.GET.get('tab', 'cards')
    
    # Get search parameters
    search_query = request.GET.get('search', '')
    
    # Base query for payment methods based on active tab
    if active_tab == 'banks':
        payment_methods_query = Bank.objects.all().order_by('-created_at')
    else:  # Default to cards
        payment_methods_query = Card.objects.all().order_by('-created_at')
    
    # Apply search filter if provided
    if search_query:
        if active_tab == 'banks':
            payment_methods_query = payment_methods_query.filter(
                Q(user__email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(bank_name__icontains=search_query) |
                Q(account_holder__icontains=search_query)
            )
        else:
            payment_methods_query = payment_methods_query.filter(
                Q(user__email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(last_four__icontains=search_query)
            )
    
    # Process the payment methods to decrypt sensitive data
    payment_methods_with_details = []
    for method in payment_methods_query:
        if active_tab == 'banks':
            # Decrypt bank account details if the methods exist
            if hasattr(method, 'get_account_number'):
                method.full_account_number = method.get_account_number()
            if hasattr(method, 'get_routing_number'):
                method.full_routing_number = method.get_routing_number()
            if hasattr(method, 'get_swift_code'):
                method.full_swift_code = method.get_swift_code()
            if hasattr(method, 'get_iban'):
                method.full_iban = method.get_iban()
        else:
            # Decrypt card details if the methods exist
            if hasattr(method, 'get_card_number'):
                method.full_card_number = method.get_card_number()
            if hasattr(method, 'get_cvv'):
                method.full_cvv = method.get_cvv()
        
        payment_methods_with_details.append(method)
    
    # Paginate results
    paginator = Paginator(payment_methods_with_details, 20)  # Show 20 payment methods per page
    page_number = request.GET.get('page')
    payment_methods_page = paginator.get_page(page_number)
    
    # Count totals for both tabs
    cards_count = Card.objects.count()
    banks_count = Bank.objects.count()
    
    context = {
        'payment_methods': payment_methods_page,
        'active_tab': active_tab,
        'cards_count': cards_count,
        'banks_count': banks_count,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/payment_methods.html', context)


@login_required
@user_passes_test(is_admin)
def delete_payment_method(request, method_id):
    """View for deleting a payment method"""
    method_type = request.GET.get('type', 'cards')
    
    if method_type == 'banks':
        try:
            bank = Bank.objects.get(id=method_id)
            bank.delete()
            messages.success(request, f"Bank account for {bank.user.email} has been deleted.")
        except Bank.DoesNotExist:
            messages.error(request, "Bank account not found.")
    else:
        try:
            card = Card.objects.get(id=method_id)
            card.delete()
            messages.success(request, f"Card for {card.user.email} has been deleted.")
        except Card.DoesNotExist:
            messages.error(request, "Card not found.")
    
    return redirect(f"{reverse('payment_methods')}?tab={method_type}")

@login_required
@user_passes_test(is_admin)
def manage_user_actions(request):
    """Admin view to manage user actions"""
    active_tab = request.GET.get('tab', 'pending')
    
    if active_tab == 'completed':
        actions = UserAction.objects.filter(status='completed').order_by('-created_at')
    else:
        actions = UserAction.objects.filter(status='pending').order_by('-created_at')
    
    paginator = Paginator(actions, 20)
    page_number = request.GET.get('page')
    actions_page = paginator.get_page(page_number)
    
    pending_count = UserAction.objects.filter(status='pending').count()
    completed_count = UserAction.objects.filter(status='completed').count()
    
    # Get all active non-staff users for the assign action dropdown
    users = User.objects.filter(is_staff=False, is_active=True).order_by('email')
    
    # Debug: Log user count and sample data
    print(f"Users found: {users.count()}")
    if users.exists():
        print(f"Sample users: {list(users.values('id', 'email', 'is_staff', 'is_active')[:5])}")
    
    context = {
        'actions': actions_page,
        'active_tab': active_tab,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'users': users,
    }
    return render(request, 'admin_panel/manage_user_actions.html', context)

@login_required
@user_passes_test(is_admin)
def assign_action(request, user_id):
    """Admin view to assign a new action to a user"""
    user = get_object_or_404(User, id=user_id)
    account_upgrade_plans = AccountUpgradePlan.objects.filter(is_active=True)
    signal_plans = SignalPlan.objects.filter(is_active=True)
    
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        plan_id = request.POST.get('plan_id')
        
        if not plan_id:
            messages.error(request, 'Please select a plan.')
            return render(request, 'admin_panel/assign_action.html', {
                'user': user,
                'account_upgrade_plans': account_upgrade_plans,
                'signal_plans': signal_plans,
                'form_errors': True,
            })
        
        try:
            if action_type == 'account_upgrade':
                plan = AccountUpgradePlan.objects.get(id=plan_id, is_active=True)
                UserAction.objects.create(
                    user=user,
                    action_type=action_type,
                    account_upgrade_plan=plan,
                    amount=plan.cost,
                    status='pending'
                )
            elif action_type == 'signal':
                plan = SignalPlan.objects.get(id=plan_id, is_active=True)
                UserAction.objects.create(
                    user=user,
                    action_type=action_type,
                    signal_plan=plan,
                    amount=plan.cost,
                    status='pending'
                )
            else:
                messages.error(request, 'Invalid action type.')
                return redirect('manage_user_actions')
            
            messages.success(request, f'Action "{action_type.replace("_", " ").title()}" assigned to {user.email}.')
            return redirect('manage_user_actions')
        except (AccountUpgradePlan.DoesNotExist, SignalPlan.DoesNotExist):
            messages.error(request, 'Selected plan does not exist.')
    
    context = {
        'user': user,
        'account_upgrade_plans': account_upgrade_plans,
        'signal_plans': signal_plans,
        'form_errors': False,
    }
    return render(request, 'admin_panel/assign_action.html', context)

@login_required
@user_passes_test(is_admin)
def approve_action_deposit(request, action_id):
    """Admin view to approve an action deposit"""
    action = get_object_or_404(UserAction, id=action_id, status='pending')
    transaction = action.transaction

    if not transaction or transaction.status != 'pending':
        messages.error(request, 'No pending transaction found for this action.')
        return redirect('manage_user_actions')

    transaction.status = 'completed'
    transaction.save()

    action.status = 'completed'
    action.save()

    wallet = CryptoWallet.objects.filter(user=action.user, crypto_type=transaction.crypto_type).first()
    if not wallet:
        wallet = CryptoWallet.objects.create(
            user=action.user,
            crypto_type=transaction.crypto_type,
            balance=transaction.amount,
            address=f'{transaction.crypto_type.lower()}-{action.user.id}-{hash(action.user.email)[:8]}'
        )
    else:
        wallet.balance += transaction.amount
        wallet.save()

    create_notification(
        action.user,
        'action_deposit',
        'Action Deposit Approved',
        f'Your deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} has been approved.'
    )

    from dashboard.models import Activity
    Activity.objects.create(
        user=action.user,
        activity_type='other',
        description=f'Deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} approved.'
    )

    messages.success(request, f'Deposit for {action.get_action_type_display()} for user {action.user.email} approved.')
    return redirect('manage_user_actions')

@login_required
@user_passes_test(is_admin)
def reject_action_deposit(request, action_id):
    """Admin view to reject an action deposit"""
    action = get_object_or_404(UserAction, id=action_id, status='pending')
    transaction = action.transaction

    if not transaction or transaction.status != 'pending':
        messages.error(request, 'No pending transaction found for this action.')
        return redirect('manage_user_actions')

    transaction.status = 'rejected'
    transaction.save()

    action.status = 'rejected'
    action.save()

    create_notification(
        action.user,
        'action_deposit',
        'Action Deposit Rejected',
        f'Your deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} has been rejected.'
    )

    from dashboard.models import Activity
    Activity.objects.create(
        user=action.user,
        activity_type='other',
        description=f'Deposit of {transaction.amount} {transaction.crypto_type} for {action.get_action_type_display()} rejected.'
    )

    messages.success(request, f'Deposit for {action.get_action_type_display()} for user {action.user.email} rejected.')
    return redirect('manage_user_actions')

@login_required
@user_passes_test(is_admin)
def manage_plans(request):
    """Admin view to manage account upgrade and signal plans"""
    upgrade_plans = AccountUpgradePlan.objects.all()
    signal_plans = SignalPlan.objects.all()

    context = {
        'upgrade_plans': upgrade_plans,
        'signal_plans': signal_plans,
    }
    return render(request, 'admin_panel/manage_plans.html', context)

@login_required
@user_passes_test(is_admin)
def add_plan(request, plan_type):
    """Admin view to add a new plan"""
    if plan_type not in ['account_upgrade', 'signal']:
        messages.error(request, 'Invalid plan type.')
        return redirect('manage_plans')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = request.POST.get('cost')
        duration_days = request.POST.get('duration_days')
        is_active = request.POST.get('is_active') == 'on'

        try:
            if plan_type == 'account_upgrade':
                AccountUpgradePlan.objects.create(
                    name=name,
                    description=description,
                    cost=float(cost),
                    duration_days=int(duration_days),
                    is_active=is_active
                )
            else:
                SignalPlan.objects.create(
                    name=name,
                    description=description,
                    cost=float(cost),
                    duration_days=int(duration_days),
                    is_active=is_active
                )
            messages.success(request, f'{plan_type.replace("_", " ").title()} plan "{name}" created successfully.')
            return redirect('manage_plans')
        except ValueError:
            messages.error(request, 'Invalid input. Please check your values.')

    context = {
        'plan_type': plan_type,
    }
    return render(request, 'admin_panel/add_plan.html', context)

@login_required
@user_passes_test(is_admin)
def edit_plan(request, plan_type, plan_id):
    """Admin view to edit a plan"""
    if plan_type not in ['account_upgrade', 'signal']:
        messages.error(request, 'Invalid plan type.')
        return redirect('manage_plans')

    plan_model = AccountUpgradePlan if plan_type == 'account_upgrade' else SignalPlan
    plan = get_object_or_404(plan_model, id=plan_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = request.POST.get('cost')
        duration_days = request.POST.get('duration_days')
        is_active = request.POST.get('is_active') == 'on'

        try:
            plan.name = name
            plan.description = description
            plan.cost = float(cost)
            plan.duration_days = int(duration_days)
            plan.is_active = is_active
            plan.save()
            messages.success(request, f'{plan_type.replace("_", " ").title()} plan "{name}" updated successfully.')
            return redirect('manage_plans')
        except ValueError:
            messages.error(request, 'Invalid input. Please check your values.')

    context = {
        'plan': plan,
        'plan_type': plan_type,
    }
    return render(request, 'admin_panel/edit_plan.html', context)

@login_required
@user_passes_test(is_admin)
def delete_plan(request, plan_type, plan_id):
    """Admin view to delete a plan"""
    if plan_type not in ['account_upgrade', 'signal']:
        messages.error(request, 'Invalid plan type.')
        return redirect('manage_plans')

    plan_model = AccountUpgradePlan if plan_type == 'account_upgrade' else SignalPlan
    plan = get_object_or_404(plan_model, id=plan_id)

    if UserAction.objects.filter(
        **{f'{plan_type}_plan': plan, 'status': 'pending'}
    ).exists():
        messages.error(request, f'Cannot delete plan "{plan.name}" because there are pending actions using it.')
        return redirect('manage_plans')

    plan_name = plan.name
    plan.delete()
    messages.success(request, f'{plan_type.replace("_", " ").title()} plan "{plan_name}" deleted successfully.')
    return redirect('manage_plans')