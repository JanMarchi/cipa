from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import (
    AccountInvitation,
    PrivilegedAccessGrant,
    Role,
    User,
    UserMembership,
    UserSession,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "is_active", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Identificação", {"fields": ("full_name",)}),
        (
            "Acesso",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "full_name", "password1", "password2")}),
    )


admin.site.register(Role)
admin.site.register(UserMembership)
admin.site.register(AccountInvitation)
admin.site.register(PrivilegedAccessGrant)
admin.site.register(UserSession)
