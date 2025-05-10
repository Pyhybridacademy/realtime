import decimal
from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return value

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    if not dictionary:
        return 0
    return dictionary.get(key, 0)

@register.filter
def crypto_to_fiat(crypto_amount, args):
    """
    Convert cryptocurrency amount to fiat currency
    Usage: {{ amount|crypto_to_fiat:"USDT,USD,exchange_rates" }}
    """
    try:
        # Parse arguments
        crypto_type, fiat_currency, exchange_rates_name = args.split(',')

        # Access exchange_rates from the template context using the variable name
        context = template.Context(dictionary={'exchange_rates': exchange_rates_name})

        # Get exchange rates from context
        exchange_rates = context['exchange_rates']

        # Get the exchange rate for this crypto and currency
        if crypto_type in exchange_rates and fiat_currency in exchange_rates[crypto_type]:
            rate = Decimal(str(exchange_rates[crypto_type][fiat_currency]))
            return Decimal(str(crypto_amount)) * rate

        return crypto_amount
    except Exception as e:
        print(f"Error in crypto_to_fiat filter: {e}")  # Add error logging
        return crypto_amount

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return Decimal(str(value)) / Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation, ZeroDivisionError):
        return value
    
@register.filter
def fiat_to_crypto(fiat_amount, args):
    """
    Convert fiat amount to cryptocurrency
    Usage: {{ amount|fiat_to_crypto:"USD,BTC,exchange_rates" }}
    """
    try:
        # Parse arguments
        fiat_currency, crypto_type, exchange_rates_var = args.split(',')
        
        # Get exchange rates from context
        exchange_rates = exchange_rates_var
        
        # Get the exchange rate for this crypto and currency
        if crypto_type in exchange_rates and fiat_currency in exchange_rates[crypto_type]:
            rate = Decimal(str(exchange_rates[crypto_type][fiat_currency]))
            if rate > 0:
                return Decimal(str(fiat_amount)) / rate
        
        return Decimal('0')
    except Exception:
        return Decimal('0')