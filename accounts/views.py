from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, ProfileForm, KYCForm, UserProfileUpdateForm, ProfileUpdateForm
from .models import Profile, KYC
from notifications.utils import create_notification
from django.contrib.auth import logout
from notifications.email_utils import notify_admin_new_account




User = get_user_model()

def home(request):
    """Home page view - shows landing page for all users"""
    context = {}
    
    if request.user.is_authenticated:
        # Add user-specific context data
        context['is_authenticated'] = True
        context['is_staff'] = request.user.is_staff
        context['is_approved'] = request.user.profile.is_approved if hasattr(request.user, 'profile') else False
    
    return render(request, 'accounts/home.html', context)



def register_step1(request):
    """First step of registration - basic user information"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Store user ID in session for step 2
            request.session['registration_user_id'] = user.id
            return redirect('register_step2')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register_step1.html', {'form': form})

def register_step2(request):
    """Second step of registration - profile information"""
    if request.user.is_authenticated:
        return redirect('home')
        
    # Check if user completed step 1
    user_id = request.session.get('registration_user_id')
    if not user_id:
        messages.error(request, 'Please complete step 1 first.')
        return redirect('register_step1')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        return redirect('register_step1')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            # Create profile for user
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Create notification for admin
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                create_notification(
                    admin,
                    'registration',
                    'New User Registration',
                    f'A new user ({user.email}) has registered and is awaiting approval.'
                )
            
            # Send email notification to admin
            from notifications.email_utils import notify_admin_new_account
            notify_admin_new_account(user)
            
            # Clear session
            if 'registration_user_id' in request.session:
                del request.session['registration_user_id']
            
            # Log the user in
            from django.contrib.auth import login
            login(request, user)
            
            return redirect('awaiting_approval')
    else:
        form = ProfileForm()
    
    return render(request, 'accounts/register_step2.html', {'form': form})

def awaiting_approval(request):
    """View for users waiting for admin approval"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff or request.user.profile.is_approved:
        return redirect('home')
    
    return render(request, 'accounts/awaiting_approval.html')

@login_required
def profile(request):
    """User profile view"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Get KYC status
    try:
        kyc = KYC.objects.get(user=request.user)
        kyc_status = kyc.status
    except KYC.DoesNotExist:
        kyc_status = 'not_submitted'
    
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'kyc_status': kyc_status
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def settings(request):
    """User settings view"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('settings')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'accounts/settings.html', context)

@login_required
def kyc_submission(request):
    """KYC document submission view"""
    if not request.user.profile.is_approved and not request.user.is_staff:
        return redirect('awaiting_approval')
    
    # Check if KYC already submitted
    try:
        kyc = KYC.objects.get(user=request.user)
        if kyc.status == 'approved':
            messages.info(request, 'Your KYC has already been approved.')
            return redirect('profile')
        elif kyc.status == 'pending':
            messages.info(request, 'Your KYC is pending approval.')
            return redirect('profile')
    except KYC.DoesNotExist:
        kyc = None
    
    if request.method == 'POST':
        form = KYCForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            kyc_submission = form.save(commit=False)
            kyc_submission.user = request.user
            kyc_submission.status = 'pending'
            kyc_submission.save()
            
            # Create notification for admin
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                create_notification(
                    admin,
                    'kyc',
                    'New KYC Submission',
                    f'User {request.user.email} has submitted KYC documents for verification.'
                )
            
            messages.success(request, 'Your KYC documents have been submitted successfully and are pending approval.')
            return redirect('profile')
    else:
        form = KYCForm(instance=kyc)
    
    return render(request, 'accounts/kyc_submission.html', {'form': form})

# Add these imports at the top if not already present
from django.shortcuts import render

# Main navigation pages
def markets(request):
    """Markets page view"""
    return render(request, 'pages/markets.html')

def about_us(request):
    """About Us page view"""
    return render(request, 'pages/about_us.html')

def insights(request):
    """Insights page view"""
    return render(request, 'pages/insights.html')

def plans(request):
    """Plans page view"""
    return render(request, 'pages/plans.html')

def contact_us(request):
    """Contact Us page view"""
    return render(request, 'pages/contact_us.html')

def professional_tools(request):
    """Professional Tools page view"""
    return render(request, 'pages/professional_tools.html')

def diverse_asset(request):
    """Diverse Asset page view"""
    return render(request, 'pages/diverse_asset.html')

# Legal and support pages
def terms_conditions(request):
    """Terms and Conditions page view"""
    return render(request, 'pages/terms_conditions.html')

def privacy_policy(request):
    """Privacy Policy page view"""
    return render(request, 'pages/privacy_policy.html')

def faqs(request):
    """FAQs page view"""
    return render(request, 'pages/faqs.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def error_404(request, exception):
    """Handle 404 (Page Not Found) errors"""
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    """Handle 500 (Server Error) errors"""
    return render(request, 'errors/500.html', status=500)

def error_403(request, exception):
    """Handle 403 (Forbidden) errors"""
    return render(request, 'errors/403.html', status=403)

def error_400(request, exception):
    """Handle 400 (Bad Request) errors"""
    return render(request, 'errors/400.html', status=400)


