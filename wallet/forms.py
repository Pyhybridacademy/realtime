from datetime import datetime
import re
from django import forms
from .models import Bank, Card

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=18, decimal_places=8, min_value=0.00000001)
    screenshot = forms.ImageField()

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(max_digits=18, decimal_places=8, min_value=0.00000001)
    withdrawal_method = forms.ChoiceField(choices=[
        ('bank', 'Bank Account'),
        ('card', 'Card'),
        ('crypto', 'Crypto Address')
    ])
    bank = forms.ModelChoiceField(queryset=None, required=False)
    card = forms.ModelChoiceField(queryset=None, required=False)
    crypto_address = forms.CharField(max_length=100, required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        withdrawal_method = cleaned_data.get('withdrawal_method')
        
        if withdrawal_method == 'bank' and not cleaned_data.get('bank'):
            self.add_error('bank', 'Please select a bank account')
        elif withdrawal_method == 'card' and not cleaned_data.get('card'):
            self.add_error('card', 'Please select a card')
        elif withdrawal_method == 'crypto' and not cleaned_data.get('crypto_address'):
            self.add_error('crypto_address', 'Please enter a crypto address')
        
        return cleaned_data

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = (
            'bank_name', 
            'account_number', 
            'account_holder',
            'routing_number',
            'swift_code',
            'iban',
            'bank_address',
            'account_type'
        )
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'account_number': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'account_holder': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'routing_number': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'swift_code': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'iban': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'bank_address': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
            'account_type': forms.Select(attrs={'class': 'shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['card_type', 'card_number', 'last_four', 'cardholder_name',
                  'expiry_date', 'cvv', 'billing_address', 'postal_code', 'is_default']
        widgets = {
            'card_type': forms.Select(attrs={
                'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md'
            }),
            'card_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': '•••• •••• •••• ••••',
                'autocomplete': 'cc-number'
            }),
            'last_four': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Last 4 digits',
                'maxlength': '4'
            }),
            'cardholder_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Name as it appears on card',
                'autocomplete': 'cc-name'
            }),
            'expiry_date': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'MM/YYYY',
                'autocomplete': 'cc-exp'
            }),
            'cvv': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': '•••',
                'maxlength': '4',
                'autocomplete': 'cc-csc'
            }),
            'billing_address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'rows': '3',
                'placeholder': 'Enter your billing address'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                'placeholder': 'Postal/ZIP code'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields not required by default
        self.fields['last_four'].required = False
        self.fields['card_number'].required = False
        
        # Make CVV optional
        self.fields['cvv'].required = False
        
        # Make billing address and postal code optional
        self.fields['billing_address'].required = False
        self.fields['postal_code'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        card_number = cleaned_data.get('card_number')
        last_four = cleaned_data.get('last_four')
        
        # Ensure either card_number or last_four is provided
        if not card_number and not last_four:
            raise forms.ValidationError("Please provide either a full card number or the last 4 digits.")
        
        # Validate card number format if provided
        if card_number:
            # Remove spaces and dashes
            card_number = card_number.replace(' ', '').replace('-', '')
            
            # Check if it's a valid number (simple check for length)
            if not card_number.isdigit():
                self.add_error('card_number', 'Card number should contain only digits.')
            elif len(card_number) < 13 or len(card_number) > 19:
                self.add_error('card_number', 'Card number should be between 13 and 19 digits.')
        
        # Validate last_four if provided
        if last_four:
            if not last_four.isdigit() or len(last_four) != 4:
                self.add_error('last_four', 'Last four digits should be exactly 4 digits.')
        
        # Validate expiry date
        expiry_date = cleaned_data.get('expiry_date')
        if expiry_date:
            try:
                # Check format MM/YYYY
                if not re.match(r'^\d{2}/\d{4}$', expiry_date):
                    self.add_error('expiry_date', 'Expiry date should be in MM/YYYY format.')
                else:
                    month, year = expiry_date.split('/')
                    month = int(month)
                    year = int(year)
                    
                    # Check if month is valid
                    if month < 1 or month > 12:
                        self.add_error('expiry_date', 'Month should be between 01 and 12.')
                    
                    # Check if the card is not expired
                    current_year = datetime.now().year
                    current_month = datetime.now().month
                    
                    if year < current_year or (year == current_year and month < current_month):
                        self.add_error('expiry_date', 'Card has expired.')
            except (ValueError, IndexError):
                self.add_error('expiry_date', 'Invalid expiry date format.')
        
        return cleaned_data
