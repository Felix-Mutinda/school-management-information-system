from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('exam/', include('exam_module.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
]
