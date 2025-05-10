from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('activities/', views.activities, name='activities'),
    path('investment-plans/', views.investment_plans, name='investment_plans'),
    path('invest/<int:plan_id>/', views.invest, name='invest'),
    path('my-investments/', views.my_investments, name='my_investments'),
    path('swap-profit/', views.swap_profit, name='swap_profit'),
    path('swap-bonus/', views.swap_bonus, name='swap_bonus'),
]