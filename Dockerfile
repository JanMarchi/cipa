FROM node:24.14.0-slim AS assets
WORKDIR /build
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY assets ./assets
COPY scripts/copy-assets.mjs ./scripts/copy-assets.mjs
RUN pnpm build

FROM python:3.13.14-slim-trixie AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN addgroup --system cipa && adduser --system --ingroup cipa cipa
COPY pyproject.toml uv.lock README.md ./
COPY apps ./apps
COPY config ./config
RUN pip install --no-cache-dir uv==0.11.15 && uv sync --frozen --no-dev --no-editable
COPY --from=assets /build/static/dist ./static/dist
COPY manage.py ./
COPY templates ./templates
COPY scripts ./scripts
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_SECRET_KEY=build-only-static-collection-key-with-more-than-fifty-characters \
    MFA_ENCRYPTION_KEYS=MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA= \
    python manage.py collectstatic --noinput && \
    chmod +x scripts/*.sh && chown -R cipa:cipa /app
USER cipa
EXPOSE 8000
ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
