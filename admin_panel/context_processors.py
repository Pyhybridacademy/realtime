from .utils import get_system_settings

def system_settings(request):
    """
    Context processor to make system settings available in all templates.
    
    Add this to your TEMPLATES context_processors in settings.py:
    'admin_panel.context_processors.system_settings',
    """
    return {
        'system_settings': get_system_settings()
    }