from django.urls import path
from . import views

urlpatterns = [
    path('actions/', views.view_actions, name='view_actions'),
]