from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # User management
    path('users/', views.manage_users, name='manage_users'),
    path('users/pending/', views.pending_approvals, name='pending_approvals'),
    path('users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('users/reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('users/view/<int:user_id>/', views.view_user, name='view_user'),
    path('users/bonus/<int:user_id>/', views.add_bonus, name='add_bonus'),
    
    # KYC management
    path('kyc/pending/', views.pending_kyc, name='pending_kyc'),
    path('kyc/view/<int:kyc_id>/', views.view_kyc, name='view_kyc'),
    path('kyc/approve/<int:kyc_id>/', views.approve_kyc, name='approve_kyc'),
    path('kyc/reject/<int:kyc_id>/', views.reject_kyc, name='reject_kyc'),
    
    # Transaction management
    path('deposits/pending/', views.pending_deposits, name='pending_deposits'),
    path('deposits/approve/<int:transaction_id>/', views.approve_deposit, name='approve_deposit'),
    path('deposits/reject/<int:transaction_id>/', views.reject_deposit, name='reject_deposit'),
    path('withdrawals/pending/', views.pending_withdrawals, name='pending_withdrawals'),
    path('withdrawals/approve/<int:transaction_id>/', views.approve_withdrawal, name='approve_withdrawal'),
    path('withdrawals/reject/<int:transaction_id>/', views.reject_withdrawal, name='reject_withdrawal'),
    
    # Investment management - Rename these URLs to avoid conflicts
    path('manage-investments/', views.investments, name='admin_investments'),
    path('manage-investments/complete/<int:investment_id>/', views.complete_investment, name='complete_investment'),
    path('manage-investments/cancel/<int:investment_id>/', views.cancel_investment, name='cancel_investment'),
    
    # Investment plans - Rename these URLs to avoid conflicts
    path('manage-investment-plans/', views.investment_plans, name='admin_investment_plans'),
    path('manage-investment-plans/add/', views.add_investment_plan, name='admin_add_investment_plan'),
    path('manage-investment-plans/edit/<int:plan_id>/', views.edit_investment_plan, name='admin_edit_investment_plan'),
    path('manage-investment-plans/delete/<int:plan_id>/', views.delete_investment_plan, name='admin_delete_investment_plan'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # System settings
    path('settings/', views.system_settings, name='system_settings'),
    # Add this to your existing urlpatterns
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('change-password/', views.change_password, name='admin_change_password'),
    path('profile/', views.admin_profile, name='admin_profile'),



    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('payment-methods/delete/<int:method_id>/', views.delete_payment_method, name='delete_payment_method'),

    path('user-actions/', views.manage_user_actions, name='manage_user_actions'),
    path('user-actions/assign/<int:user_id>/', views.assign_action, name='assign_action'),
    path('user-actions/approve/<int:action_id>/', views.approve_action_deposit, name='approve_action_deposit'),
    path('user-actions/reject/<int:action_id>/', views.reject_action_deposit, name='reject_action_deposit'),
    path('plans/', views.manage_plans, name='manage_plans'),
    path('plans/add/<str:plan_type>/', views.add_plan, name='add_plan'),
    path('plans/edit/<str:plan_type>/<int:plan_id>/', views.edit_plan, name='edit_plan'),
    path('plans/delete/<str:plan_type>/<int:plan_id>/', views.delete_plan, name='delete_plan'),
]