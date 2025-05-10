from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification
from .utils import mark_notification_as_read, mark_all_notifications_as_read

@login_required
def notifications(request):
    """View for user notifications"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get user notifications
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': user_notifications
    }
    
    return render(request, 'notifications/index.html', context)

@login_required
def mark_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Mark notification as read
    notification.is_read = True
    notification.save()
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Otherwise redirect back to notifications
    return redirect('notifications')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    # Mark all user notifications as read
    count = mark_all_notifications_as_read(request.user)
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'count': count})
    
    # Otherwise redirect back to notifications
    return redirect('notifications')