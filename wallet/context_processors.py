from admin_panel.utils import get_exchange_rates

def exchange_rates(request):
    """
    Context processor to add exchange rates to all templates
    """
    return {
        'exchange_rates': get_exchange_rates()
    }