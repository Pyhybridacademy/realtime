from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from admin_panel.models import SystemSettings
from django.utils import timezone


def get_system_settings():
    """Get system settings or use defaults from settings.py"""
    try:
        system_settings = SystemSettings.get_settings()
        return {
            'site_name': system_settings.site_name,
            'support_email': system_settings.contact_email or settings.DEFAULT_FROM_EMAIL,
            'admin_email': system_settings.contact_email or settings.DEFAULT_FROM_EMAIL,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }
    except:
        # Fallback to settings.py
        return {
            'site_name': getattr(settings, 'SITE_NAME', 'Investment Platform'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
            'admin_email': getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

# Admin notifications
def notify_admin_new_account(user):
    """Notify admin about new user registration"""
    system_settings = get_system_settings()
    
    subject = f'New User Registration: {user.email}'
    # Use hardcoded URL instead of reverse
    admin_url = f"{system_settings['site_url']}/admin/users/"
    
    context = {
        'user': user,
        'profile': user.profile,
        'admin_url': admin_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/admin_new_account.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [system_settings['admin_email']],
        html_message=html_message,
        fail_silently=True,
    )

def notify_admin_deposit(transaction):
    """Notify admin about new deposit"""
    system_settings = get_system_settings()
    
    subject = f'New Deposit: {transaction.amount} {transaction.crypto_type} from {transaction.user.email}'
    # Use hardcoded URL instead of reverse
    admin_url = f"{system_settings['site_url']}/admin/transactions/deposits/"
    
    context = {
        'user': transaction.user,
        'transaction': transaction,
        'admin_url': admin_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/admin_deposit.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [system_settings['admin_email']],
        html_message=html_message,
        fail_silently=True,
    )

def notify_admin_withdrawal(transaction):
    """Notify admin about new withdrawal request"""
    system_settings = get_system_settings()
    
    subject = f'New Withdrawal Request: {transaction.amount} {transaction.crypto_type} from {transaction.user.email}'
    # Use hardcoded URL instead of reverse
    admin_url = f"{system_settings['site_url']}/admin/transactions/withdrawals/"
    
    context = {
        'user': transaction.user,
        'transaction': transaction,
        'admin_url': admin_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/admin_withdrawal.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [system_settings['admin_email']],
        html_message=html_message,
        fail_silently=True,
    )

def notify_admin_investment(investment):
    """Notify admin about new investment"""
    system_settings = get_system_settings()
    
    subject = f'New Investment: {investment.amount} USDT from {investment.user.email}'
    # Use hardcoded URL instead of reverse
    admin_url = f"{system_settings['site_url']}/admin/investments/"
    
    context = {
        'user': investment.user,
        'investment': investment,
        'admin_url': admin_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/admin_investment.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [system_settings['admin_email']],
        html_message=html_message,
        fail_silently=True,
    )

# User notifications
def notify_user_account_approved(user):
    """Notify user that their account has been approved"""
    system_settings = get_system_settings()
    
    subject = f'{system_settings["site_name"]} - Your Account Has Been Approved'
    
    try:
        login_url = f"{system_settings['site_url']}{reverse('login')}"
    except:
        login_url = f"{system_settings['site_url']}/accounts/login/"
    
    context = {
        'user': user,
        'login_url': login_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/user_account_approved.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )

def notify_user_deposit_approved(transaction):
    """Notify user that their deposit has been approved"""
    system_settings = get_system_settings()
    
    subject = f'{system_settings["site_name"]} - Your Deposit Has Been Approved'
    
    try:
        dashboard_url = f"{system_settings['site_url']}{reverse('dashboard')}"
    except:
        dashboard_url = f"{system_settings['site_url']}/dashboard/"
    
    try:
        balance = transaction.user.balance
    except:
        # If there's no direct balance attribute, we'll just pass the transaction
        balance = None
    
    context = {
        'user': transaction.user,
        'transaction': transaction,
        'balance': balance,
        'dashboard_url': dashboard_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/user_deposit_approved.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [transaction.user.email],
        html_message=html_message,
        fail_silently=True,
    )

def notify_user_withdrawal_approved(transaction):
    """Notify user that their withdrawal has been approved"""
    system_settings = get_system_settings()
    
    subject = f'{system_settings["site_name"]} - Your Withdrawal Has Been Processed'
    
    try:
        dashboard_url = f"{system_settings['site_url']}{reverse('dashboard')}"
    except:
        dashboard_url = f"{system_settings['site_url']}/dashboard/"
    
    try:
        balance = transaction.user.balance
    except:
        # If there's no direct balance attribute, we'll just pass the transaction
        balance = None
    
    context = {
        'user': transaction.user,
        'transaction': transaction,
        'balance': balance,
        'dashboard_url': dashboard_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/user_withdrawal_approved.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [transaction.user.email],
        html_message=html_message,
        fail_silently=True,
    )

def notify_user_investment_completed(investment):
    """Notify user that their investment has been completed"""
    system_settings = get_system_settings()
    
    subject = f'{system_settings["site_name"]} - Your Investment Has Been Completed'
    
    try:
        dashboard_url = f"{system_settings['site_url']}{reverse('dashboard')}"
    except:
        dashboard_url = f"{system_settings['site_url']}/dashboard/"
    
    try:
        balance = investment.user.balance
    except:
        # If there's no direct balance attribute, we'll just pass the investment
        balance = None
    
    context = {
        'user': investment.user,
        'investment': investment,
        'balance': balance,
        'dashboard_url': dashboard_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email']
    }
    
    html_message = render_to_string('emails/user_investment_completed.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [investment.user.email],
        html_message=html_message,
        fail_silently=True,
    )

def notify_user_bonus(user, amount, currency):
    """Notify user that a bonus has been added to their account"""
    system_settings = get_system_settings()
    
    subject = f'{system_settings["site_name"]} - Bonus Added to Your Account'
    
    try:
        dashboard_url = f"{system_settings['site_url']}{reverse('dashboard')}"
    except:
        dashboard_url = f"{system_settings['site_url']}/dashboard/"
    
    try:
        balance = user.balance
    except:
        # If there's no direct balance attribute, we'll just pass None
        balance = None
    
    context = {
        'user': user,
        'amount': amount,
        'currency': currency,
        'balance': balance,
        'dashboard_url': dashboard_url,
        'site_name': system_settings['site_name'],
        'support_email': system_settings['support_email'],
        'now': timezone.now()
    }
    
    html_message = render_to_string('emails/user_bonus.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )
