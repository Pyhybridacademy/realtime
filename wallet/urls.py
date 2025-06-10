from django.urls import path
from . import views

urlpatterns = [
    path('wallet_overview/', views.wallet_overview, name='wallet_overview'),
    path('deposit/<int:wallet_id>/', views.deposit, name='deposit'),
    path('deposit/<int:wallet_id>/<int:action_id>/', views.deposit, name='deposit'),
    path('withdraw/<int:wallet_id>/', views.withdraw, name='withdraw'),
    path('add-bank/', views.add_bank, name='add_bank'),
    path('edit-bank/<int:bank_id>/', views.edit_bank, name='edit_bank'),
    path('delete-bank/<int:bank_id>/', views.delete_bank, name='delete_bank'),
    path('add-card/', views.add_card, name='add_card'),
    path('edit-card/<int:card_id>/', views.edit_card, name='edit_card'),
    path('delete-card/<int:card_id>/', views.delete_card, name='delete_card'),
]