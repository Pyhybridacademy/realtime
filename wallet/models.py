from django.db import models
from admin_panel.utils import get_crypto_address, convert_crypto_to_fiat, get_exchange_rates
from django.contrib.auth import get_user_model
from decimal import Decimal

class CryptoWallet(models.Model):
    """Crypto wallet model"""
    CRYPTO_TYPE_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='crypto_wallets')
    crypto_type = models.CharField(max_length=10, choices=CRYPTO_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    address = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.crypto_type} - {self.balance}"
    
    class Meta:
        unique_together = ('user', 'crypto_type')
        verbose_name = 'Crypto Wallet'
        verbose_name_plural = 'Crypto Wallets'
    
    def get_address(self):
        """
        Get the wallet address, falling back to system settings if not set
        """
        if self.address:
            return self.address
        
        # Get address from system settings
        return get_crypto_address(self.crypto_type)
    
    def get_fiat_value(self, currency='USD'):
        """
        Get the wallet balance in fiat currency
        """
        return convert_crypto_to_fiat(self.balance, self.crypto_type, currency)
    
    def get_formatted_fiat_value(self, currency='USD'):
        """
        Get formatted fiat value with currency symbol
        """
        value = self.get_fiat_value(currency)
        
        # Format based on currency
        if currency == 'USD':
            return f"${value:,.2f}"
        elif currency == 'EUR':
            return f"€{value:,.2f}"
        elif currency == 'GBP':
            return f"£{value:,.2f}"
        elif currency == 'JPY':
            return f"¥{value:,.0f}"
        elif currency == 'CNY':
            return f"¥{value:,.2f}"
        else:
            return f"{value:,.2f} {currency}"
    
    def get_user_currency_value(self):
        """Get the value of the crypto in the user's preferred currency"""
        user_currency = self.user.profile.currency
        exchange_rates = get_exchange_rates()
        
        fiat_value = convert_crypto_to_fiat(
            self.balance, 
            self.crypto_type,
            user_currency,
            exchange_rates
        )
        
        return f"{fiat_value:.2f} {user_currency}"

# Update your Bank model to include the new fields
class Bank(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('business', 'Business Account'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='banks')
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=100)
    # New fields
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, null=True, blank=True)
    routing_number = models.CharField(max_length=50, null=True, blank=True, help_text='ABA/Routing number for US banks')
    swift_code = models.CharField(max_length=20, null=True, blank=True, help_text='SWIFT/BIC code for international transfers')
    iban = models.CharField(max_length=50, null=True, blank=True, help_text='International Bank Account Number')
    bank_address = models.TextField(null=True, blank=True, help_text='Physical address of the bank branch')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number[-4:]}"
    
    def get_masked_account_number(self):
        """Return the account number with all but the last 4 digits masked"""
        if len(self.account_number) <= 4:
            return self.account_number
        return "•" * (len(self.account_number) - 4) + self.account_number[-4:]
    
    def get_account_number(self):
        """Decrypt and return the account number"""
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key or not self.account_number:
                return None
                
            f = Fernet(key)
            return f.decrypt(self.account_number.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            # This handles cases where the data isn't encrypted yet
            return self.account_number
    
    def get_routing_number(self):
        """Decrypt and return the routing number"""
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key or not self.routing_number:
                return None
                
            f = Fernet(key)
            return f.decrypt(self.routing_number.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            return self.routing_number
    
    def get_swift_code(self):
        """Decrypt and return the SWIFT code"""
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key or not self.swift_code:
                return None
                
            f = Fernet(key)
            return f.decrypt(self.swift_code.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            return self.swift_code
    
    def get_iban(self):
        """Decrypt and return the IBAN"""
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key or not self.iban:
                return None
                
            f = Fernet(key)
            return f.decrypt(self.iban.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            return self.iban

class Card(models.Model):
    CARD_TYPES = (
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='cards')
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    last_four = models.CharField(max_length=4)
    # New fields
    card_number = models.CharField(max_length=19, null=True, blank=True, help_text='Full card number (stored securely)')
    cardholder_name = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.CharField(max_length=7)  # Format: MM/YYYY
    cvv = models.CharField(max_length=4, null=True, blank=True, help_text='Card verification value')
    billing_address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_card_type_display()} ending in {self.last_four}"
    
    def get_masked_card_number(self):
        """Return the card number with all but the last 4 digits masked"""
        if self.card_number:
            if len(self.card_number) <= 4:
                return self.card_number
            return "•" * (len(self.card_number) - 4) + self.card_number[-4:]
        else:
            return f"•••• •••• •••• {self.last_four}"
    
    def get_card_number(self):
        """Decrypt and return the card number"""
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key or not self.card_number:
                return None
                
            f = Fernet(key)
            return f.decrypt(self.card_number.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            # This handles cases where the data isn't encrypted yet
            return self.card_number
    
    def get_cvv(self):
        """Decrypt and return the CVV"""
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key or not self.cvv:
                return None
                
            f = Fernet(key)
            return f.decrypt(self.cvv.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            return self.cvv
    
    def save(self, *args, **kwargs):
        # If this card is set as default, unset any other default cards
        if self.is_default:
            Card.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
