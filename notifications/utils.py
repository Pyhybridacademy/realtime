from .models import Notification

def create_notification(user, notification_type, title, message):
    """
    Create a notification for a user.
    
    Args:
        user: The user to create the notification for
        notification_type: Type of notification (deposit, withdrawal, approval, etc.)
        title: Title of the notification
        message: Message content of the notification
    
    Returns:
        The created notification object
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message
    )
    
    return notification

def get_unread_notifications_count(user):
    """
    Get the count of unread notifications for a user.
    
    Args:
        user: The user to get the count for
    
    Returns:
        The count of unread notifications
    """
    return Notification.objects.filter(user=user, is_read=False).count()

def mark_notification_as_read(notification_id):
    """
    Mark a notification as read.
    
    Args:
        notification_id: The ID of the notification to mark as read
    
    Returns:
        True if successful, False otherwise
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False

def mark_all_notifications_as_read(user):
    """
    Mark all notifications for a user as read.
    
    Args:
        user: The user to mark all notifications as read for
    
    Returns:
        The number of notifications marked as read
    """
    unread_notifications = Notification.objects.filter(user=user, is_read=False)
    count = unread_notifications.count()
    unread_notifications.update(is_read=True)
    return count