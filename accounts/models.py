from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django_countries.fields import CountryField

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom User model with email as the unique identifier."""
    username = None
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    """User profile model"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    CURRENCY_CHOICES = (
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('ZAR', 'South African Rands'),
        ('CNY', 'Chinese Yuan'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
    )
    
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)
    country = CountryField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='USD')
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    ssn = models.CharField(max_length=20, blank=True, null=True)  # Adding SSN field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.country.name}"

class KYC(models.Model):
    """KYC verification model"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='kyc')
    id_document = models.FileField(upload_to='kyc/id_documents/')
    address_proof = models.FileField(upload_to='kyc/address_proofs/')
    additional_document = models.FileField(upload_to='kyc/additional_documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.status}"
    
    class Meta:
        verbose_name = 'KYC'
        verbose_name_plural = 'KYCs'