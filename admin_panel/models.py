from django.db import models

class SystemSettings(models.Model):
    # Site Settings
    site_name = models.CharField(max_length=100, default="Investment Platform")
    site_description = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    
    # Social Media Links
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    
    # Email Settings
    email_host = models.CharField(max_length=100, blank=True, null=True)
    email_port = models.IntegerField(default=587)
    email_host_user = models.CharField(max_length=100, blank=True, null=True)
    email_host_password = models.CharField(max_length=100, blank=True, null=True)
    email_use_tls = models.BooleanField(default=True)
    default_from_email = models.EmailField(blank=True, null=True)
    
    # Payment Settings
    btc_address = models.CharField(max_length=100, blank=True, null=True)
    eth_address = models.CharField(max_length=100, blank=True, null=True)
    usdt_address = models.CharField(max_length=100, blank=True, null=True)
    
    # Referral Settings
    enable_referrals = models.BooleanField(default=True)
    referral_bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    # KYC Settings
    kyc_required = models.BooleanField(default=True)
    kyc_documents_required = models.TextField(blank=True, null=True, 
                                             default="ID Card, Proof of Address, Selfie")
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True, 
                                          default="We are currently performing maintenance. Please check back later.")
    
    # System Settings
    min_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    withdrawal_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.50)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings