from django import forms
from .models import UserAction

class ActionDepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=18, decimal_places=8, min_value=0.00000001)
    screenshot = forms.ImageField()
    crypto_type = forms.ChoiceField(choices=[
        ('USDT', 'Tether'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
    ])