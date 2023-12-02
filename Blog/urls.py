from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="Blog-about"),
    path("follow/", views.follow, name="Blog-follow"),
]
