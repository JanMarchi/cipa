from django.db import connections


class PostgresOnlyMigrationRouter:
    def allow_migrate(
        self, db: str, app_label: str, model_name: str | None = None, **hints: object
    ) -> bool | None:
        if hints.get("target_db") == "postgresql":
            return connections[db].vendor == "postgresql"
        return None
