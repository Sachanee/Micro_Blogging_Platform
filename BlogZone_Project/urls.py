from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("Blog.urls")),
    path('login/', auth_views.LoginView
         .as_view(template_name='users/login.html'), name='login'),
    path('register/', users_views.register, name='register-users'),
]
