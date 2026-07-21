#!/bin/sh
set -eu
export DATABASE_URL="${DATABASE_MIGRATION_URL:?DATABASE_MIGRATION_URL is required}"
exec "$@"
