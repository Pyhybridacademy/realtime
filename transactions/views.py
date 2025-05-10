from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Transaction
from accounts.models import User
from wallet.models import CryptoWallet

@login_required
def transactions(request):
    """View all transactions for the logged-in user"""
    transaction_type = request.GET.get('type')
    
    if transaction_type:
        transactions_list = Transaction.objects.filter(
            user=request.user, 
            transaction_type=transaction_type
        ).order_by('-created_at')
    else:
        transactions_list = Transaction.objects.filter(
            user=request.user
        ).order_by('-created_at')
    
    paginator = Paginator(transactions_list, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
    return render(request, 'transactions/transactions.html', {
        'transactions': transactions,
        'current_type': transaction_type
    })

@login_required
def transaction_detail(request, transaction_id):
    """View details of a specific transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    return render(request, 'transactions/transaction_detail.html', {
        'transaction': transaction
    })

@login_required
def create_withdrawal(request, wallet_id=None):
    """Create a withdrawal transaction"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
        
    wallet = None
    if wallet_id:
        wallet = get_object_or_404(CryptoWallet, id=wallet_id, user=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        crypto_type = request.POST.get('crypto_type')
        wallet_id = request.POST.get('wallet_id')
        withdrawal_address = request.POST.get('withdrawal_address')
        
        if not wallet_id:
            messages.error(request, 'Please select a wallet')
            return redirect('create_withdrawal')
        
        wallet = get_object_or_404(CryptoWallet, id=wallet_id, user=request.user)
        
        # Check if user has enough balance
        if float(amount) > wallet.balance:
            messages.error(request, 'Insufficient balance')
            return redirect('create_withdrawal')
        
        # Create the transaction
        transaction = Transaction.objects.create(
            user=request.user,
            transaction_type='withdrawal',
            amount=amount,
            crypto_type=crypto_type,
            status='pending',
            withdrawal_details=f"Withdrawal Address: {withdrawal_address}"
        )
        
        messages.success(request, 'Withdrawal request submitted successfully. Please wait for admin approval.')
        return redirect('transaction_detail', transaction_id=transaction.id)
    
    # If wallet_id is not provided, get all user wallets for selection
    wallets = CryptoWallet.objects.filter(user=request.user)
    
    return render(request, 'transactions/create_withdrawal.html', {
        'wallet': wallet,
        'wallets': wallets
    })