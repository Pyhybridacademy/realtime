from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class AccountUpgradePlan(models.Model):
    """Model for account upgrade plans"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=18, decimal_places=8)  # Cost in USDT
    duration_days = models.PositiveIntegerField()  # Duration of the upgrade
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.cost} USDT for {self.duration_days} days"

    class Meta:
        verbose_name = "Account Upgrade Plan"
        verbose_name_plural = "Account Upgrade Plans"

class SignalPlan(models.Model):
    """Model for signal purchase plans"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=18, decimal_places=8)  # Cost in USDT
    duration_days = models.PositiveIntegerField()  # Duration of signal access
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.cost} USDT for {self.duration_days} days"

    class Meta:
        verbose_name = "Signal Plan"
        verbose_name_plural = "Signal Plans"

class UserAction(models.Model):
    """Model to track user actions (account upgrade or signal purchase)"""
    ACTION_TYPE_CHOICES = (
        ('account_upgrade', 'Account Upgrade'),
        ('signal_purchase', 'Signal Purchase'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    account_upgrade_plan = models.ForeignKey(AccountUpgradePlan, on_delete=models.SET_NULL, null=True, blank=True)
    signal_plan = models.ForeignKey(SignalPlan, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=8)  # Amount to be paid in USDT
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_action_type_display()} - {self.status}"

    class Meta:
        verbose_name = "User Action"
        verbose_name_plural = "User Actions"