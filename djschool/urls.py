from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('exam/', include('exam_module.urls')),
    path('', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
