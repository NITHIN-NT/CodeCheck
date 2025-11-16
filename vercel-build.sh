#!/usr/bin/env bash
set -euo pipefail

echo ">>> Running vercel-build.sh"

# Ensure pip and dependencies are available
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run Django collectstatic to populate staticfiles/
python manage.py collectstatic --noinput

echo ">>> collectstatic finished. Listing staticfiles root:"
ls -la staticfiles | sed -n '1,200p'
