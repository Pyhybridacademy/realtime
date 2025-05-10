from django.db import models

class Transaction(models.Model):
    """Transaction model"""
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('profit', 'Profit'),
        ('bonus', 'Bonus'),
        ('investment', 'Investment'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    CRYPTO_TYPE_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('', 'None'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    currency = models.CharField(max_length=10)
    crypto_type = models.CharField(max_length=10, choices=CRYPTO_TYPE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    withdrawal_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount} {self.currency} - {self.status}"