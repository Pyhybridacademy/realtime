from .utils import get_unread_notifications_count

def notifications(request):
    """
    Context processor to add notification data to all templates.
    """
    if request.user.is_authenticated:
        unread_count = get_unread_notifications_count(request.user)
        return {
            'unread_notifications_count': unread_count
        }
    return {
        'unread_notifications_count': 0
    }