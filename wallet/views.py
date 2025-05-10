from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import CryptoWallet, Bank, Card
from .forms import DepositForm, WithdrawalForm, BankForm, CardForm
from transactions.models import Transaction
from notifications.utils import create_notification
from admin_panel.utils import get_exchange_rates, convert_crypto_to_fiat, convert_fiat_to_crypto
from notifications.email_utils import notify_admin_deposit, notify_admin_withdrawal

User = get_user_model()

@login_required
def wallet_overview(request):
    """Wallet overview page"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')

    # Get user's crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(user=request.user)

    # Check if user has no wallets, create default ones
    if not crypto_wallets.exists():
        # Create default wallets for BTC, ETH, and USDT
        CryptoWallet.objects.create(user=request.user, crypto_type='BTC', balance=Decimal('0.0'))
        CryptoWallet.objects.create(user=request.user, crypto_type='ETH', balance=Decimal('0.0'))
        CryptoWallet.objects.create(user=request.user, crypto_type='USDT', balance=Decimal('0.0'))
        
        # Refresh the wallets queryset
        crypto_wallets = CryptoWallet.objects.filter(user=request.user)

    # Get user's banks and cards
    banks = Bank.objects.filter(user=request.user)
    cards = Card.objects.filter(user=request.user)

    # Get exchange rates
    exchange_rates = get_exchange_rates()
    
    # Get user's preferred currency
    user_currency = request.user.profile.currency
    
    # Calculate fiat equivalents for each wallet
    wallet_equivalents = []
    total_fiat_value = Decimal('0.0')
    
    for wallet in crypto_wallets:
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

    context = {
        'wallets': crypto_wallets,
        'wallet_equivalents': wallet_equivalents,
        'total_fiat_value': total_fiat_value,
        'banks': banks,
        'cards': cards,
        'exchange_rates': exchange_rates,
        'user_currency': user_currency
    }

    return render(request, 'wallet/wallet_overview.html', context)


@login_required
def deposit(request, wallet_id):
    """Deposit to wallet view"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    wallet = get_object_or_404(CryptoWallet, id=wallet_id, user=request.user)
    
    if request.method == 'POST':
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            screenshot = form.cleaned_data['screenshot']
            
            # Create transaction record
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=amount,
                currency=wallet.crypto_type,
                crypto_type=wallet.crypto_type,
                status='pending',
                screenshot=screenshot
            )
            
            # Create notification for admin
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                create_notification(
                    admin,
                    'deposit',
                    'New Deposit Request',
                    f'User {request.user.email} has submitted a deposit request for {amount} {wallet.crypto_type}.'
                )
            
            # Create notification for user
            create_notification(
                request.user,
                'deposit',
                'Deposit Request Submitted',
                f'Your deposit request for {amount} {wallet.crypto_type} has been submitted and is pending approval.'
            )
            
            # Send email notification to admin
            from notifications.email_utils import notify_admin_deposit
            notify_admin_deposit(transaction)
            
            messages.success(request, f'Your deposit request for {amount} {wallet.crypto_type} has been submitted and is pending approval.')
            return redirect('wallet_overview')
    else:
        form = DepositForm()
    
    context = {
        'wallet': wallet,
        'form': form
    }
    
    return render(request, 'wallet/deposit.html', context)

@login_required
def withdraw(request, wallet_id):
    """Withdraw from wallet view"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    wallet = get_object_or_404(CryptoWallet, id=wallet_id, user=request.user)
    banks = Bank.objects.filter(user=request.user)
    cards = Card.objects.filter(user=request.user)
    
    # Initialize form with user's banks and cards
    form = WithdrawalForm()
    form.fields['bank'].queryset = banks
    form.fields['card'].queryset = cards
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        form.fields['bank'].queryset = banks
        form.fields['card'].queryset = cards
        
        if form.is_valid():
            amount = form.cleaned_data['amount']
            withdrawal_method = form.cleaned_data['withdrawal_method']
            
            # Check if user has enough balance
            if amount > wallet.balance:
                messages.error(request, f'Insufficient balance. Your current balance is {wallet.balance} {wallet.crypto_type}.')
                return redirect('withdraw', wallet_id=wallet.id)
            
            # Create transaction record
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='withdrawal',
                amount=amount,
                currency=wallet.crypto_type,
                crypto_type=wallet.crypto_type,
                status='pending'
            )
            
            # Add withdrawal method details
            if withdrawal_method == 'bank':
                bank = form.cleaned_data['bank']
                transaction.withdrawal_details = f"Bank: {bank.bank_name}, Account: {bank.account_number}"
            elif withdrawal_method == 'card':
                card = form.cleaned_data['card']
                transaction.withdrawal_details = f"Card: {card.card_type}, Last Four: {card.last_four}"
            elif withdrawal_method == 'crypto':
                crypto_address = form.cleaned_data['crypto_address']
                transaction.withdrawal_details = f"Crypto Address: {crypto_address}"
            
            transaction.save()
            
            # Create notification for admin
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                create_notification(
                    admin,
                    'withdrawal',
                    'New Withdrawal Request',
                    f'User {request.user.email} has submitted a withdrawal request for {amount} {wallet.crypto_type}.'
                )
            
            # Create notification for user
            create_notification(
                request.user,
                'withdrawal',
                'Withdrawal Request Submitted',
                f'Your withdrawal request for {amount} {wallet.crypto_type} has been submitted and is pending approval.'
            )
            
            # Send email notification to admin
            from notifications.email_utils import notify_admin_withdrawal
            notify_admin_withdrawal(transaction)
            
            messages.success(request, f'Your withdrawal request for {amount} {wallet.crypto_type} has been submitted and is pending approval.')
            return redirect('wallet_overview')
    
    context = {
        'wallet': wallet,
        'form': form,
        'banks': banks,
        'cards': cards
    }
    
    return render(request, 'wallet/withdraw.html', context)


@login_required
def add_bank(request):
    """View for adding a bank account"""
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.user = request.user
            bank.save()
            messages.success(request, "Bank account added successfully.")
            return redirect('wallet_overview')
    else:
        form = BankForm()
    
    return render(request, 'wallet/add_bank.html', {'form': form})

@login_required
def add_card(request):
    """View for adding a payment card"""
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            
            # If full card number is provided, extract last four
            card_number = form.cleaned_data.get('card_number')
            if card_number and len(card_number) >= 4:
                card.last_four = card_number[-4:]
            
            # If this card is set as default, unset any other default cards
            if card.is_default:
                Card.objects.filter(user=request.user, is_default=True).update(is_default=False)
                
            card.save()
            messages.success(request, "Card added successfully.")
            return redirect('wallet_overview')
        else:
            # Add this line to show form errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = CardForm()
    
    # Move this return outside the else block so it works for both GET and invalid POST
    return render(request, 'wallet/add_card.html', {'form': form})

@login_required
def edit_bank(request, bank_id):
    """View for editing a bank account"""
    bank = get_object_or_404(Bank, id=bank_id, user=request.user)
    
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, "Bank account updated successfully.")
            return redirect('wallet_overview')
    else:
        form = BankForm(instance=bank)
    
    return render(request, 'wallet/edit_bank.html', {'form': form, 'bank': bank})

@login_required
def edit_card(request, card_id):
    """View for editing a payment card"""
    card = get_object_or_404(Card, id=card_id, user=request.user)
    
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            card = form.save(commit=False)
            
            # If full card number is provided, extract last four
            if card.card_number:
                card.last_four = card.card_number[-4:]
            
            card.save()
            messages.success(request, "Card updated successfully.")
            return redirect('wallet_overview')
    else:
        form = CardForm(instance=card)
    
    return render(request, 'wallet/edit_card.html', {'form': form, 'card': card})

@login_required
def delete_bank(request, bank_id):
    """View for deleting a bank account"""
    bank = get_object_or_404(Bank, id=bank_id, user=request.user)
    
    if request.method == 'POST':
        bank.delete()
        messages.success(request, "Bank account deleted successfully.")
    
    return redirect('wallet_overview')

@login_required
def delete_card(request, card_id):
    """View for deleting a payment card"""
    card = get_object_or_404(Card, id=card_id, user=request.user)
    
    if request.method == 'POST':
        card.delete()
        messages.success(request, "Card deleted successfully.")
    
    return redirect('wallet_overview')
