from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from datetime import timedelta
from decimal import Decimal
from wallet.models import CryptoWallet
from transactions.models import Transaction
from .models import Investment, Balance, InvestmentPlan, Activity
from admin_panel.utils import get_exchange_rates, convert_crypto_to_fiat, convert_fiat_to_crypto
from notifications.email_utils import notify_admin_investment

@login_required
def dashboard(request):
    """Main dashboard view"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user's crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(user=request.user)
    
    # Check if user has no wallets, create default ones
    if not crypto_wallets.exists():
        # Create default wallets for BTC, ETH, and USDT
        CryptoWallet.objects.create(user=request.user, crypto_type='BTC', balance=0)
        CryptoWallet.objects.create(user=request.user, crypto_type='ETH', balance=0)
        CryptoWallet.objects.create(user=request.user, crypto_type='USDT', balance=0)
        
        # Refresh the wallets queryset
        crypto_wallets = CryptoWallet.objects.filter(user=request.user)
    
    # Get exchange rates
    exchange_rates = get_exchange_rates()
    
    # Get user's preferred currency
    user_currency = request.user.profile.currency
    
    # Get user's balance
    try:
        balance = Balance.objects.get(user=request.user)
    except Balance.DoesNotExist:
        # Create default balance if it doesn't exist
        balance = Balance.objects.create(
            user=request.user,
            total=Decimal('0.0'),
            deposit=Decimal('0.0'),
            profit=Decimal('0.0'),
            bonus=Decimal('0.0')
        )
    
    # Calculate fiat equivalents for each wallet
    wallet_equivalents = []
    total_fiat_value = Decimal('0.0')
    
    for wallet in crypto_wallets:
        if wallet.balance > 0:
            # Get the fiat value for this wallet
            fiat_value = convert_crypto_to_fiat(
                wallet.balance, 
                wallet.crypto_type, 
                user_currency, 
                exchange_rates
            )
            
            wallet_equivalents.append({
                'wallet': wallet,
                'fiat_value': fiat_value
            })
            
            total_fiat_value += fiat_value
    
    # Create a dictionary with both crypto and fiat values
    fiat_balance = {
        'total': total_fiat_value,
        'profit': convert_crypto_to_fiat(balance.profit, 'USDT', user_currency, exchange_rates),
        'bonus': convert_crypto_to_fiat(balance.bonus, 'USDT', user_currency, exchange_rates),
        'deposit': convert_crypto_to_fiat(balance.deposit, 'USDT', user_currency, exchange_rates)
    }
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get recent deposits
    recent_deposits = Transaction.objects.filter(
        user=request.user, 
        transaction_type='deposit',
        status='completed'
    ).order_by('-created_at')[:2]
    
    # Get user's investments
    investments = Investment.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Calculate profit statistics
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Daily profit (last 24 hours)
    daily_profit_crypto = Transaction.objects.filter(
        user=request.user,
        transaction_type='profit',
        status='completed',
        created_at__gte=timezone.now() - timedelta(days=1)
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0')
    
    daily_profit = convert_crypto_to_fiat(daily_profit_crypto, 'USDT', user_currency, exchange_rates)
    
    # Monthly profit
    monthly_profit_crypto = Transaction.objects.filter(
        user=request.user,
        transaction_type='profit',
        status='completed',
        created_at__date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0')
    
    monthly_profit = convert_crypto_to_fiat(monthly_profit_crypto, 'USDT', user_currency, exchange_rates)
    
    # Previous month profit for comparison
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    prev_month_profit_crypto = Transaction.objects.filter(
        user=request.user,
        transaction_type='profit',
        status='completed',
        created_at__date__gte=prev_month_start,
        created_at__date__lt=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0')
    
    prev_month_profit = convert_crypto_to_fiat(prev_month_profit_crypto, 'USDT', user_currency, exchange_rates)
    
    # Calculate profit growth percentage
    if prev_month_profit > 0:
        profit_growth = ((monthly_profit - prev_month_profit) / prev_month_profit) * 100
        # Convert to float for template rendering
        profit_growth = float(profit_growth)
    else:
        profit_growth = 100 if monthly_profit > 0 else 0
    
    # Calculate referral and loyalty bonuses
    referral_bonus_crypto = Transaction.objects.filter(
        user=request.user,
        transaction_type='bonus',
        status='completed',
        created_at__date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0')
    
    referral_bonus = convert_crypto_to_fiat(referral_bonus_crypto, 'USDT', user_currency, exchange_rates)
    
    loyalty_bonus_crypto = balance.bonus - referral_bonus_crypto if balance.bonus > referral_bonus_crypto else Decimal('0.0')
    loyalty_bonus = convert_crypto_to_fiat(loyalty_bonus_crypto, 'USDT', user_currency, exchange_rates)
    
    # Calculate crypto equivalents for the total balance
    btc_equivalent = convert_fiat_to_crypto(total_fiat_value, user_currency, 'BTC', exchange_rates)
    eth_equivalent = convert_fiat_to_crypto(total_fiat_value, user_currency, 'ETH', exchange_rates)
    usdt_equivalent = convert_fiat_to_crypto(total_fiat_value, user_currency, 'USDT', exchange_rates)
    
    context = {
        'crypto_wallets': crypto_wallets,
        'wallet_equivalents': wallet_equivalents,
        'recent_transactions': recent_transactions,
        'recent_deposits': recent_deposits,
        'investments': investments,
        'balance': balance,  # Original crypto balance
        'fiat_balance': fiat_balance,  # Fiat equivalent balance
        'exchange_rates': exchange_rates,
        'daily_profit': daily_profit,
        'monthly_profit': monthly_profit,
        'profit_growth': round(profit_growth, 2),
        'referral_bonus': referral_bonus,
        'loyalty_bonus': loyalty_bonus,
        'btc_equivalent': btc_equivalent,
        'eth_equivalent': eth_equivalent,
        'usdt_equivalent': usdt_equivalent
    }
    
    return render(request, 'dashboard/index.html', context)

# Helper function to convert fiat to crypto
def convert_fiat_to_crypto(amount, fiat_currency, crypto_type, exchange_rates):
    """Convert fiat amount to crypto equivalent"""
    from decimal import Decimal
    
    if amount <= 0 or not exchange_rates or crypto_type not in exchange_rates:
        return Decimal('0.0')
    
    # Convert amount to Decimal if it's not already
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    # If the fiat currency is USD, direct conversion
    if fiat_currency == 'USD' and 'USD' in exchange_rates[crypto_type]:
        crypto_to_usd = Decimal(str(exchange_rates[crypto_type]['USD']))
        return amount / crypto_to_usd if crypto_to_usd > 0 else Decimal('0.0')
    
    # For other currencies, first convert to USD then to crypto
    if fiat_currency in exchange_rates[crypto_type]:
        fiat_to_crypto = Decimal(str(exchange_rates[crypto_type][fiat_currency]))
        return amount / fiat_to_crypto if fiat_to_crypto > 0 else Decimal('0.0')
    
    # If we don't have direct conversion rates, try to use USD as a fallback
    if 'USD' in exchange_rates[crypto_type]:
        crypto_to_usd = Decimal(str(exchange_rates[crypto_type]['USD']))
        return amount / crypto_to_usd if crypto_to_usd > 0 else Decimal('0.0')
    
    return Decimal('0.0')

@login_required
def transactions(request):
    """View for all user transactions"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get all user transactions
    all_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'transactions': all_transactions
    }
    
    return render(request, 'dashboard/transactions.html', context)

@login_required
def activities(request):
    """View for user activity log"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user activities
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')
    
    context = {
        'activities': activities
    }
    
    return render(request, 'dashboard/activities.html', context)

@login_required
def investment_plans(request):
    """View available investment plans"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user's crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(user=request.user)
    
    # Get exchange rates
    exchange_rates = get_exchange_rates()
    user_currency = request.user.profile.currency
    
    # Calculate fiat equivalents for each wallet
    wallet_equivalents = []
    total_fiat_value = Decimal('0.0')
    
    for wallet in crypto_wallets:
        if wallet.balance > 0:
            fiat_value = convert_crypto_to_fiat(
                wallet.balance, 
                wallet.crypto_type, 
                user_currency, 
                exchange_rates
            )
            
            wallet_equivalents.append({
                'wallet': wallet,
                'fiat_value': fiat_value
            })
            
            total_fiat_value += fiat_value
    
    # Get available plans
    plans = InvestmentPlan.objects.filter(is_active=True).order_by('minimum_amount')
    
    # Get user's active investments
    active_investments = Investment.objects.filter(
        user=request.user,
        status='active'
    ).select_related('plan').order_by('-created_at')
    
    # Calculate total invested amount (in user's currency)
    total_invested = Decimal('0.0')
    for investment in Investment.objects.filter(user=request.user):
        total_invested += convert_crypto_to_fiat(
            investment.amount,
            'USDT',  # Assuming investments are stored in USDT
            user_currency,
            exchange_rates
        )
    
    # Calculate total profit (in user's currency)
    total_profit = Decimal('0.0')
    for investment in Investment.objects.filter(user=request.user, status='completed'):
        profit = investment.amount * investment.plan.return_percentage / 100
        total_profit += convert_crypto_to_fiat(
            profit,
            'USDT',
            user_currency,
            exchange_rates
        )
    
    context = {
        'plans': plans,
        'active_investments': active_investments,
        'wallet_equivalents': wallet_equivalents,
        'total_fiat_value': total_fiat_value,
        'total_invested': total_invested,
        'total_profit': total_profit,
        'user_currency': user_currency,
        'exchange_rates': exchange_rates,
    }
    
    return render(request, 'dashboard/investment_plans.html', context)

@login_required
def invest(request, plan_id):
    """View for investing in a plan"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    plan = get_object_or_404(InvestmentPlan, id=plan_id, is_active=True)
    
    # Get user's crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(user=request.user)
    
    # Get exchange rates
    exchange_rates = get_exchange_rates()
    user_currency = request.user.profile.currency
    
    # Calculate fiat equivalents for each wallet
    wallet_equivalents = []
    total_fiat_value = Decimal('0.0')
    
    for wallet in crypto_wallets:
        if wallet.balance > 0:
            fiat_value = convert_crypto_to_fiat(
                wallet.balance, 
                wallet.crypto_type, 
                user_currency, 
                exchange_rates
            )
            
            wallet_equivalents.append({
                'wallet': wallet,
                'fiat_value': fiat_value
            })
            
            total_fiat_value += fiat_value
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(str(amount))  # Convert to Decimal for precise calculations
            
            # Validate amount
            if amount < plan.minimum_amount:
                messages.error(request, f'Minimum investment amount is {plan.minimum_amount} {user_currency}.')
                return redirect('invest', plan_id=plan.id)
            
            if amount > plan.maximum_amount:
                messages.error(request, f'Maximum investment amount is {plan.maximum_amount} {user_currency}.')
                return redirect('invest', plan_id=plan.id)
            
            # Check if user has enough balance in wallet equivalents
            if amount > total_fiat_value:
                messages.error(request, f'Insufficient balance. Your current equivalent balance is {total_fiat_value} {user_currency}.')
                return redirect('invest', plan_id=plan.id)
            
            # Calculate expected profit
            expected_profit = amount * (plan.return_percentage / 100)
            
            # Convert investment amount from fiat to USDT (assuming investments are stored in USDT)
            usdt_amount = convert_fiat_to_crypto(amount, user_currency, 'USDT', exchange_rates)
            
            # Deduct from wallets based on priority (USDT first, then ETH, then BTC)
            remaining_usdt_to_deduct = usdt_amount
            wallets_by_type = {wallet.crypto_type: wallet for wallet in crypto_wallets}
            
            # Try to deduct from USDT wallet first
            if 'USDT' in wallets_by_type and remaining_usdt_to_deduct > 0:
                usdt_wallet = wallets_by_type['USDT']
                usdt_in_wallet = usdt_wallet.balance
                usdt_to_deduct = min(usdt_in_wallet, remaining_usdt_to_deduct)
                
                if usdt_to_deduct > 0:
                    usdt_wallet.balance -= usdt_to_deduct
                    usdt_wallet.save()
                    remaining_usdt_to_deduct -= usdt_to_deduct
            
            # If we still need to deduct more, convert from ETH
            if 'ETH' in wallets_by_type and remaining_usdt_to_deduct > 0:
                eth_wallet = wallets_by_type['ETH']
                eth_in_wallet = eth_wallet.balance
                eth_value_in_usdt = convert_crypto_to_fiat(eth_in_wallet, 'ETH', 'USD', exchange_rates)
                
                if eth_value_in_usdt > 0:
                    eth_to_deduct = min(eth_in_wallet, convert_fiat_to_crypto(remaining_usdt_to_deduct, 'USDT', 'ETH', exchange_rates))
                    
                    if eth_to_deduct > 0:
                        eth_wallet.balance -= eth_to_deduct
                        eth_wallet.save()
                        
                        usdt_value_of_eth = convert_crypto_to_fiat(eth_to_deduct, 'ETH', 'USD', exchange_rates)
                        remaining_usdt_to_deduct -= usdt_value_of_eth
            
            # If we still need to deduct more, convert from BTC
            if 'BTC' in wallets_by_type and remaining_usdt_to_deduct > 0:
                btc_wallet = wallets_by_type['BTC']
                btc_in_wallet = btc_wallet.balance
                btc_to_deduct = min(btc_in_wallet, convert_fiat_to_crypto(remaining_usdt_to_deduct, 'USDT', 'BTC', exchange_rates))
                
                if btc_to_deduct > 0:
                    btc_wallet.balance -= btc_to_deduct
                    btc_wallet.save()
            
            # Create investment
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=plan.duration_days)
            investment = Investment.objects.create(
                user=request.user,
                plan=plan,
                amount=usdt_amount,  # Store in USDT
                expected_profit=expected_profit,  # Add expected profit
                status='active',
                start_date=start_date,
                end_date=end_date
            )
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='investment',
                amount=usdt_amount,
                currency='USDT',  # Store in USDT
                status='completed'
            )
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='investment',
                description=f'Invested {amount} {user_currency} in {plan.name} plan.'
            )
            
            # Create notification
            from notifications.utils import create_notification
            create_notification(
                request.user,
                'investment',
                'Investment Created',
                f'Your investment of {amount} {user_currency} in {plan.name} plan has been created successfully.'
            )
            
            # Send email notification to admin
            from notifications.email_utils import notify_admin_investment
            notify_admin_investment(investment)
            
            messages.success(request, f'Your investment of {amount} {user_currency} in {plan.name} plan has been created successfully.')
            return redirect('investment_plans')
            
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Invalid amount: {str(e)}')
            return redirect('invest', plan_id=plan.id)
    
    context = {
        'plan': plan,
        'wallet_equivalents': wallet_equivalents,
        'total_fiat_value': total_fiat_value,
        'user_currency': user_currency
    }
    
    return render(request, 'dashboard/invest.html', context)

@login_required
def my_investments(request):
    """View for user's investments"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user's investments
    active_investments = Investment.objects.filter(user=request.user, status='active').order_by('-created_at')
    completed_investments = Investment.objects.filter(user=request.user, status='completed').order_by('-updated_at')
    
    context = {
        'active_investments': active_investments,
        'completed_investments': completed_investments
    }
    
    return render(request, 'dashboard/my_investments.html', context)

@login_required
def notifications(request):
    """View for user notifications"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Import the Notification model - add this to your imports at the top of the file
    from notifications.models import Notification
    
    # Get user notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications
    }
    
    return render(request, 'dashboard/notifications.html', context)

@login_required
def mark_read(request, notification_id):
    """Mark a notification as read"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Import the Notification model
    from notifications.models import Notification
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return redirect('notifications')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Import the Notification model
    from notifications.models import Notification
    
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return redirect('notifications')


@login_required
def swap_profit(request):
    """View for swapping profit to a crypto wallet"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user's balance
    try:
        balance = Balance.objects.get(user=request.user)
    except Balance.DoesNotExist:
        messages.error(request, 'Balance not found.')
        return redirect('dashboard')
    
    # Get user's crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(user=request.user)
    
    # Get exchange rates
    exchange_rates = get_exchange_rates()
    user_currency = request.user.profile.currency
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        crypto_type = request.POST.get('crypto_type')
        
        try:
            amount = Decimal(str(amount))
            
            # Validate amount
            if amount <= 0:
                messages.error(request, 'Amount must be greater than zero.')
                return redirect('swap_profit')
            
            if amount > balance.profit:
                messages.error(request, f'Insufficient profit balance. Your current profit balance is {balance.profit} USDT.')
                return redirect('swap_profit')
            
            # Get the target wallet
            try:
                target_wallet = CryptoWallet.objects.get(user=request.user, crypto_type=crypto_type)
            except CryptoWallet.DoesNotExist:
                messages.error(request, f'{crypto_type} wallet not found.')
                return redirect('swap_profit')
            
            # Convert USDT amount to target crypto
            crypto_amount = convert_fiat_to_crypto(amount, 'USDT', crypto_type, exchange_rates)
            
            # Update balances
            balance.profit -= amount
            balance.total -= amount  # Decrease total balance
            balance.save()
            
            # Update wallet
            target_wallet.balance += crypto_amount
            target_wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='swap',
                amount=amount,
                currency='USDT',
                status='completed',
                description=f'Swapped {amount} USDT profit to {crypto_amount} {crypto_type}'
            )
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='other',
                description=f'Swapped {amount} USDT profit to {crypto_amount} {crypto_type}'
            )
            
            messages.success(request, f'Successfully swapped {amount} USDT profit to {crypto_amount} {crypto_type}')
            return redirect('dashboard')
            
        except (ValueError, TypeError):
            messages.error(request, 'Swapped successfully.')
            return redirect('swap_profit')
    
    context = {
        'balance': balance,
        'crypto_wallets': crypto_wallets,
        'user_currency': user_currency
    }
    
    return render(request, 'dashboard/swap_profit.html', context)

@login_required
def swap_bonus(request):
    """View for swapping bonus to a crypto wallet"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user's balance
    try:
        balance = Balance.objects.get(user=request.user)
    except Balance.DoesNotExist:
        messages.error(request, 'Balance not found.')
        return redirect('dashboard')
    
    # Get user's crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(user=request.user)
    
    # Get exchange rates
    exchange_rates = get_exchange_rates()
    user_currency = request.user.profile.currency
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        crypto_type = request.POST.get('crypto_type')
        
        try:
            amount = Decimal(str(amount))
            
            # Validate amount
            if amount <= 0:
                messages.error(request, 'Amount must be greater than zero.')
                return redirect('swap_bonus')
            
            if amount > balance.bonus:
                messages.error(request, f'Insufficient bonus balance. Your current bonus balance is {balance.bonus} USDT.')
                return redirect('swap_bonus')
            
            # Get the target wallet
            try:
                target_wallet = CryptoWallet.objects.get(user=request.user, crypto_type=crypto_type)
            except CryptoWallet.DoesNotExist:
                messages.error(request, f'{crypto_type} wallet not found.')
                return redirect('swap_bonus')
            
            # Convert USDT amount to target crypto
            crypto_amount = convert_fiat_to_crypto(amount, 'USDT', crypto_type, exchange_rates)
            
            # Update balances
            balance.bonus -= amount
            balance.total -= amount  # Decrease total balance
            balance.save()
            
            # Update wallet
            target_wallet.balance += crypto_amount
            target_wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='swap',
                amount=amount,
                currency='USDT',
                status='completed',
                description=f'Swapped {amount} USDT bonus to {crypto_amount} {crypto_type}'
            )
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='other',
                description=f'Swapped {amount} USDT bonus to {crypto_amount} {crypto_type}'
            )
            
            messages.success(request, f'Successfully swapped {amount} USDT bonus to {crypto_amount} {crypto_type}')
            return redirect('dashboard')
            
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount.')
            return redirect('swap_bonus')
    
    context = {
        'balance': balance,
        'crypto_wallets': crypto_wallets,
        'user_currency': user_currency
    }
    
    return render(request, 'dashboard/swap_bonus.html', context)
