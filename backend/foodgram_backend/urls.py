from django.contrib import admin
from django.urls import path, include

from api.utils import get_short_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:pk>/', get_short_url, name='short_url')
]
