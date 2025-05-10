from django.core.cache import cache
from django.conf import settings
from .models import SystemSettings
from decimal import Decimal
import logging
import requests
from datetime import datetime, timedelta
import json
from django.conf import settings

logger = logging.getLogger(__name__)

# Cache timeout in seconds (default: 5 minutes)
SETTINGS_CACHE_TIMEOUT = getattr(settings, 'SETTINGS_CACHE_TIMEOUT', 300)
SETTINGS_CACHE_KEY = 'system_settings'

def get_system_settings(refresh=False):
    """
    Get all system settings as a dictionary.
    
    Args:
        refresh (bool): Force refresh from database instead of using cache
        
    Returns:
        dict: Dictionary containing all system settings
    """
    if not refresh:
        # Try to get from cache first
        cached_settings = cache.get(SETTINGS_CACHE_KEY)
        if cached_settings:
            return cached_settings
    
    try:
        # Get from database
        settings_obj = SystemSettings.get_settings()
        
        # Convert model instance to dictionary
        settings_dict = {}
        for field in settings_obj._meta.fields:
            field_name = field.name
            if field_name not in ['id', 'created_at', 'updated_at']:
                settings_dict[field_name] = getattr(settings_obj, field_name)
        
        # Store in cache
        cache.set(SETTINGS_CACHE_KEY, settings_dict, SETTINGS_CACHE_TIMEOUT)
        return settings_dict
    
    except Exception as e:
        logger.error(f"Error retrieving system settings: {str(e)}")
        return {}

def get_setting(key, default=None, refresh=False):
    """
    Get a specific system setting by key.
    
    Args:
        key (str): The setting key to retrieve
        default: Default value if setting doesn't exist
        refresh (bool): Force refresh from database
        
    Returns:
        The setting value or default if not found
    """
    settings_dict = get_system_settings(refresh=refresh)
    return settings_dict.get(key, default)

def get_boolean_setting(key, default=False, refresh=False):
    """
    Get a boolean system setting.
    
    Args:
        key (str): The setting key to retrieve
        default (bool): Default value if setting doesn't exist
        refresh (bool): Force refresh from database
        
    Returns:
        bool: The setting value as boolean
    """
    value = get_setting(key, default, refresh)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', 'yes', '1', 'on']
    return bool(value)

def get_int_setting(key, default=0, refresh=False):
    """
    Get an integer system setting.
    
    Args:
        key (str): The setting key to retrieve
        default (int): Default value if setting doesn't exist
        refresh (bool): Force refresh from database
        
    Returns:
        int: The setting value as integer
    """
    value = get_setting(key, default, refresh)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def get_decimal_setting(key, default=Decimal('0.0'), refresh=False):
    """
    Get a decimal system setting.
    
    Args:
        key (str): The setting key to retrieve
        default (Decimal): Default value if setting doesn't exist
        refresh (bool): Force refresh from database
        
    Returns:
        Decimal: The setting value as Decimal
    """
    value = get_setting(key, default, refresh)
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default

def update_setting(key, value):
    """
    Update a specific system setting.
    
    Args:
        key (str): The setting key to update
        value: The new value
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        settings_obj = SystemSettings.get_settings()
        
        # Check if the field exists
        if hasattr(settings_obj, key):
            setattr(settings_obj, key, value)
            settings_obj.save(update_fields=[key])
            
            # Invalidate cache
            cache.delete(SETTINGS_CACHE_KEY)
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating system setting '{key}': {str(e)}")
        return False

def update_settings(settings_dict):
    """
    Update multiple system settings at once.
    
    Args:
        settings_dict (dict): Dictionary of settings to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        settings_obj = SystemSettings.get_settings()
        update_fields = []
        
        for key, value in settings_dict.items():
            if hasattr(settings_obj, key):
                setattr(settings_obj, key, value)
                update_fields.append(key)
        
        if update_fields:
            settings_obj.save(update_fields=update_fields)
            
            # Invalidate cache
            cache.delete(SETTINGS_CACHE_KEY)
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating multiple system settings: {str(e)}")
        return False

def refresh_settings_cache():
    """
    Force refresh the settings cache.
    
    Returns:
        dict: Updated settings dictionary
    """
    return get_system_settings(refresh=True)

def get_site_name():
    """
    Convenience function to get site name.
    
    Returns:
        str: Site name
    """
    return get_setting('site_name', 'Investment Platform')

def get_contact_email():
    """
    Convenience function to get contact email.
    
    Returns:
        str: Contact email
    """
    return get_setting('contact_email', '')

def get_crypto_address(crypto_type):
    """
    Get payment address for a specific cryptocurrency.
    
    Args:
        crypto_type (str): Type of cryptocurrency (BTC, ETH, USDT, etc.)
        
    Returns:
        str: Wallet address or empty string if not found
    """
    crypto_type = crypto_type.lower()
    address_key = f"{crypto_type}_address"
    return get_setting(address_key, '')

def is_maintenance_mode():
    """
    Check if maintenance mode is enabled.
    
    Returns:
        bool: True if maintenance mode is enabled
    """
    return get_boolean_setting('maintenance_mode', False)

def get_min_withdrawal():
    """
    Get minimum withdrawal amount.
    
    Returns:
        Decimal: Minimum withdrawal amount
    """
    return get_decimal_setting('min_withdrawal', Decimal('50.00'))

def get_withdrawal_fee_percentage():
    """
    Get withdrawal fee percentage.
    
    Returns:
        Decimal: Withdrawal fee percentage
    """
    return get_decimal_setting('withdrawal_fee_percentage', Decimal('2.50'))

def is_referral_enabled():
    """
    Check if referral program is enabled.
    
    Returns:
        bool: True if referral program is enabled
    """
    return get_boolean_setting('enable_referrals', True)

def get_referral_bonus_percentage():
    """
    Get referral bonus percentage.
    
    Returns:
        Decimal: Referral bonus percentage
    """
    return get_decimal_setting('referral_bonus_percentage', Decimal('5.00'))

def is_kyc_required():
    """
    Check if KYC verification is required.
    
    Returns:
        bool: True if KYC verification is required
    """
    return get_boolean_setting('kyc_required', True)

def get_crypto_address(crypto_type):
    """Get crypto address from system settings"""
    settings = SystemSettings.get_settings()
    if crypto_type == 'BTC':
        return settings.btc_address
    elif crypto_type == 'ETH':
        return settings.eth_address
    elif crypto_type == 'USDT':
        return settings.usdt_address
    return None

def get_exchange_rates():
    """
    Fetches exchange rates for BTC, ETH, and USDT against USD, EUR, GBP, and ZAR from the CryptoCompare API.
    Returns a dictionary of exchange rates.
    """
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,USDT&tsyms=USD,EUR,GBP,ZAR&api_key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        exchange_rates = {
            'BTC': data.get('BTC', {'USD': 50000, 'EUR': 45000, 'GBP': 40000, 'ZAR': 900000}),
            'ETH': data.get('ETH', {'USD': 3000, 'EUR': 2700, 'GBP': 2400, 'ZAR': 54000}),
            'USDT': data.get('USDT', {'USD': 1, 'EUR': 0.9, 'GBP': 0.8, 'ZAR': 18})
        }
        exchange_rates['last_updated'] = datetime.now()
        return exchange_rates

    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates: {e}")
        # Fallback to default rates in case of API error
        default_rates = {
            'BTC': {'USD': 50000, 'EUR': 45000, 'GBP': 40000, 'ZAR': 900000},
            'ETH': {'USD': 3000, 'EUR': 2700, 'GBP': 2400, 'ZAR': 54000},
            'USDT': {'USD': 1, 'EUR': 0.9, 'GBP': 0.8, 'ZAR': 18},
            'last_updated': datetime.now()
        }
        return default_rates

if __name__ == '__main__':
    rates = get_exchange_rates()
    print(rates)


def convert_crypto_to_fiat(crypto_amount, crypto_type, fiat_currency, exchange_rates=None):
    """
    Convert cryptocurrency amount to fiat currency
    """
    if crypto_amount <= 0:
        return Decimal('0.0')
    
    if exchange_rates is None:
        exchange_rates = get_exchange_rates()
    
    # Convert crypto_amount to Decimal if it's not already
    if not isinstance(crypto_amount, Decimal):
        crypto_amount = Decimal(str(crypto_amount))
    
    # Check if we have the exchange rate data
    if crypto_type not in exchange_rates or fiat_currency not in exchange_rates[crypto_type]:
        # Default to USD if the requested currency is not available
        if crypto_type in exchange_rates and 'USD' in exchange_rates[crypto_type]:
            # Convert float to Decimal before multiplication
            return crypto_amount * Decimal(str(exchange_rates[crypto_type]['USD']))
        return crypto_amount  # Return the original amount if no conversion is possible
    
    # Convert float to Decimal before multiplication
    return crypto_amount * Decimal(str(exchange_rates[crypto_type][fiat_currency]))

def convert_fiat_to_crypto(amount, fiat_currency, crypto_type, exchange_rates=None):
    """
    Convert fiat amount to crypto equivalent
    """
    if amount <= 0:
        return Decimal('0.0')
    
    if exchange_rates is None:
        exchange_rates = get_exchange_rates()
    
    # Check if we have the exchange rate data
    if crypto_type not in exchange_rates:
        return Decimal('0.0')
    
    # Convert amount to Decimal if it's not already
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    # If the fiat currency is USD, direct conversion
    if fiat_currency == 'USD' and 'USD' in exchange_rates[crypto_type]:
        crypto_to_usd = Decimal(str(exchange_rates[crypto_type]['USD']))
        return amount / crypto_to_usd if crypto_to_usd > 0 else Decimal('0.0')
    
    # For other currencies, check if direct conversion is available
    if fiat_currency in exchange_rates[crypto_type]:
        fiat_to_crypto = Decimal(str(exchange_rates[crypto_type][fiat_currency]))
        return amount / fiat_to_crypto if fiat_to_crypto > 0 else Decimal('0.0')
    
    # If direct conversion is not available, try to convert via USD
    if 'USD' in exchange_rates[crypto_type]:
        crypto_to_usd = Decimal(str(exchange_rates[crypto_type]['USD']))
        # Assume 1:1 conversion if we don't have specific rates
        return amount / crypto_to_usd if crypto_to_usd > 0 else Decimal('0.0')
    
    return Decimal('0.0')