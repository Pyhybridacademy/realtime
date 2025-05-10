from django.db import models

class Notification(models.Model):
    """Notification model"""
    NOTIFICATION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('approval', 'Approval'),
        ('kyc', 'KYC'),
        ('investment', 'Investment'),
        ('bonus', 'Bonus'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.notification_type} - {self.is_read}"
    
    class Meta:
        ordering = ['-created_at']