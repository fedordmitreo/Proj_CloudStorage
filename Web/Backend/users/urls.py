# cloud_drive/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls')),
]