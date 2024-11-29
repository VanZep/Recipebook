from django.contrib import admin
from django.urls import path, include

from api.utils import short_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:pk>/', short_url, name='short_url')
]
