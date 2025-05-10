from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from .models import Profile, KYC

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    country = CountryField().formfield()
    
    class Meta:
        model = Profile
        fields = ('country', 'currency', 'zip_code', 'city', 'phone_number', 'gender', 'ssn')
        widgets = {
            'currency': forms.Select(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'}),
            'gender': forms.Select(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'}),
        }

class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ('id_document', 'address_proof', 'additional_document')
        widgets = {
            'id_document': forms.FileInput(attrs={'class': 'sr-only', 'accept': 'image/*,application/pdf'}),
            'address_proof': forms.FileInput(attrs={'class': 'sr-only', 'accept': 'image/*,application/pdf'}),
            'additional_document': forms.FileInput(attrs={'class': 'sr-only', 'accept': 'image/*,application/pdf'}),
        }

class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('country', 'currency', 'zip_code', 'city', 'phone_number', 'gender', 'profile_photo')
        widgets = {
            'currency': forms.Select(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'}),
            'gender': forms.Select(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'}),
        }