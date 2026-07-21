from django.urls import path

from apps.core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/live/", views.live, name="health-live"),
    path("health/ready/", views.ready, name="health-ready"),
    path("app/<slug:tenant_slug>/dashboard/", views.dashboard, name="dashboard"),
]
