from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        '',
        include('news.urls')
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path(
        'api-token-auth/',
        obtain_auth_token,
        name='api_token_auth'
    ),
]