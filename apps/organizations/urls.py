from django.urls import path

from apps.organizations import views

urlpatterns = [
    path("", views.company_list, name="company-list"),
    path("nova/", views.company_create, name="company-create"),
]
