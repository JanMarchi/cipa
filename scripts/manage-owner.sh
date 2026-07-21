#!/bin/sh
set -eu
exec ./scripts/owner-command.sh python manage.py "$@"
