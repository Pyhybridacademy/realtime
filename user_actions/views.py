from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserAction

@login_required
def view_actions(request):
    """User view to display pending actions"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        messages.warning(request, 'Your account is awaiting approval.')
        return redirect('awaiting_approval')

    pending_actions = UserAction.objects.filter(user=request.user, status='pending').order_by('-created_at')
    context = {
        'pending_actions': pending_actions,
    }
    return render(request, 'user_actions/view_actions.html', context)