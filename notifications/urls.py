from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),  # This is the important line
    path('mark_read/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('mark_all_read/', views.mark_all_read, name='mark_all_read'),
]