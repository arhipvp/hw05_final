from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace='posts')),
    path('about/', include('about.urls', namespace='about')),
]

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'
handler500 = 'core.views.server_error'