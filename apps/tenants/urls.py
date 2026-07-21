from django.urls import path

from apps.tenants import views

urlpatterns = [path("selecionar-contexto/", views.select_tenant, name="tenant-select")]
