from django.urls import path

from apps.establishments import views

urlpatterns = [
    path("", views.establishment_list, name="establishment-list"),
    path("novo/", views.establishment_create, name="establishment-create"),
]
