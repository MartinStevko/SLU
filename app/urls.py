from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('tournament/', include('tournament.urls')),
    path('registration/', include('registration.urls')),
    path('', include('content.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
