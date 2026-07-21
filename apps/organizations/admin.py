from django.contrib import admin

from apps.organizations.models import Company, Organization

admin.site.register(Organization)
admin.site.register(Company)
