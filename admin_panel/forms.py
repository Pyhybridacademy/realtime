from django import forms
from .models import SystemSettings
from django.contrib.auth import get_user_model
from accounts.models import Profile, KYC
from dashboard.models import Balance
from wallet.models import CryptoWallet
from django_countries.fields import CountryField

User = get_user_model()

class AdminEditUserForm(forms.ModelForm):
    """Form for admin to edit basic user information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded'
            }),
        }

class AdminEditProfileForm(forms.ModelForm):
    """Form for admin to edit user profile information"""
    country = CountryField().formfield()
    
    class Meta:
        model = Profile
        fields = ['phone_number', 'country', 'city', 'zip_code', 'gender', 'currency', 'is_approved', 'ssn']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'city': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'gender': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'currency': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'is_approved': forms.CheckboxInput(attrs={
                'class': 'focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded'
            }),
            'ssn': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
        }

class AdminEditBalanceForm(forms.ModelForm):
    """Form for admin to edit user balance information"""
    class Meta:
        model = Balance
        fields = ['total', 'deposit', 'profit', 'bonus']
        widgets = {
            'total': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'step': '0.01'
            }),
            'deposit': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'step': '0.01'
            }),
            'profit': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'step': '0.01'
            }),
            'bonus': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'step': '0.01'
            }),
        }

class AdminEditKYCForm(forms.ModelForm):
    """Form for admin to edit KYC status"""
    class Meta:
        model = KYC
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm'
            }),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'rows': 3
            }),
        }

class AdminEditCryptoWalletForm(forms.ModelForm):
    """Form for admin to edit crypto wallet balance"""
    class Meta:
        model = CryptoWallet
        fields = ['balance']
        widgets = {
            'balance': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'step': '0.00000001'
            }),
        }


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        exclude = ['created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap/Tailwind classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring focus:ring-primary-500 focus:ring-opacity-50'
            
            # Add placeholders
            if field_name == 'site_name':
                field.widget.attrs['placeholder'] = 'Your Site Name'
            elif field_name == 'site_description':
                field.widget.attrs['placeholder'] = 'Brief description of your platform'
            elif field_name == 'contact_email':
                field.widget.attrs['placeholder'] = 'contact@example.com'
            elif field_name == 'contact_phone':
                field.widget.attrs['placeholder'] = '+1 (123) 456-7890'
            elif field_name == 'contact_address':
                field.widget.attrs['placeholder'] = 'Your business address'
            elif 'address' in field_name:
                field.widget.attrs['placeholder'] = f'Your {field_name.split("_")[0].upper()} wallet address'
            elif field_name == 'email_host':
                field.widget.attrs['placeholder'] = 'smtp.example.com'
            elif field_name == 'email_host_user':
                field.widget.attrs['placeholder'] = 'username@example.com'
            elif field_name == 'email_host_password':
                field.widget.attrs['placeholder'] = '••••••••'
                field.widget.attrs['type'] = 'password'