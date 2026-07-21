from typing import Any

from django.http import HttpRequest


def tenant_context(request: HttpRequest) -> dict[str, Any]:
    return {"active_tenant": getattr(request, "tenant", None)}
