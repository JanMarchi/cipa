from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from django.db import connection, transaction

from apps.core.context import tenant_id_var, user_id_var


def set_database_context(*, tenant_id: UUID | None, user_id: UUID | None) -> None:
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.user_id', %s, true)", [str(user_id or "")])
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(tenant_id or "")])


@contextmanager
def tenant_context(*, tenant_id: UUID, user_id: UUID | None = None) -> Iterator[None]:
    tenant_token = tenant_id_var.set(str(tenant_id))
    user_token = user_id_var.set(str(user_id or ""))
    try:
        with transaction.atomic():
            set_database_context(tenant_id=tenant_id, user_id=user_id)
            yield
    finally:
        tenant_id_var.reset(tenant_token)
        user_id_var.reset(user_token)
