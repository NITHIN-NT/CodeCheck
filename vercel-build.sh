#!/usr/bin/env bash
set -euo pipefail

echo ">>> vercel-build.sh starting"

# Tell settings.py we're in build mode so it uses IS_BUILD paths (no DB)
export VERCEL_BUILD=1
export DJANGO_SETTINGS_MODULE=review_dashboard.settings
export PYTHONUNBUFFERED=1

echo ">>> Environment:"
echo "VERCEL_BUILD=$VERCEL_BUILD"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Install dependencies (Vercel already runs `pip install -r requirements.txt` by default,
# but run again in case the build uses separate steps)
python -m pip install --upgrade pip || true
python -m pip install -r requirements.txt

# Run collectstatic. With VERCEL_BUILD=1 your settings should avoid DB access.
python manage.py collectstatic --noinput

echo ">>> collectstatic finished. staticfiles contents:"
ls -la staticfiles || true
