from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

class Balance(models.Model):
    """User balance model"""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='balance')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deposit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.total}"


User = get_user_model()

class InvestmentPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    minimum_amount = models.DecimalField(max_digits=18, decimal_places=8)  
    maximum_amount = models.DecimalField(max_digits=18, decimal_places=8)  
    return_percentage = models.DecimalField(max_digits=8, decimal_places=2)  # Percentage return
    duration_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.return_percentage}% in {self.duration_days} days"
    
    @property
    def daily_profit_percentage(self):
        """Calculate daily profit percentage"""
        if self.duration_days > 0:
            return self.return_percentage / self.duration_days
        return Decimal('0.0')

class Investment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=18, decimal_places=8)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.plan.name} Investment"
    
    @property
    def expected_profit(self):
        """Calculate expected profit in USDT"""
        return self.amount * self.plan.return_percentage / 100
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.status != 'active':
            return 100 if self.status == 'completed' else 0
            
        total_days = (self.end_date - self.start_date).days
        if total_days <= 0:
            return 0
            
        days_passed = (timezone.now().date() - self.start_date).days
        progress = min(100, max(0, (days_passed / total_days) * 100))
        return round(progress)
    
class Activity(models.Model):
    """User activity log model"""
    ACTIVITY_TYPE_CHOICES = (
        ('login', 'Login'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
        ('profile_update', 'Profile Update'),
        ('kyc', 'KYC Submission'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.timestamp}"
    
    class Meta:
        verbose_name_plural = 'Activities'