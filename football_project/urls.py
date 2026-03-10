from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported here!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # This routes all /api/... requests to your app
]