from django import forms
from .models import SystemSettings

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