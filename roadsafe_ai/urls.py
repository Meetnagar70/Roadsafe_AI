# roadsafe_ai/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure to import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')), # Add this line
]