from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from config import settings
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns (
    path('admin/', admin.site.urls),
    path('', include('online_shop.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('rosetta/', include('rosetta.urls')),
    # path('i18n/', include('django.conf.urls.i18n'))
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)