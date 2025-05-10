from django.urls import path
from . import views

urlpatterns = [
    path('', views.transactions, name='transactions'),
    path('<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('withdraw/<int:wallet_id>/', views.create_withdrawal, name='create_withdrawal'),
]