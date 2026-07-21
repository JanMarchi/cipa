from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contas/", include("allauth.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
    path("app/", include("apps.tenants.urls")),
    path("empresas/", include("apps.organizations.urls")),
    path("estabelecimentos/", include("apps.establishments.urls")),
    path("auditoria/", include("apps.audit.urls")),
]
