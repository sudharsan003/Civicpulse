# civicpulse/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('issues.urls')),  # This links everything from issues.urls
]
