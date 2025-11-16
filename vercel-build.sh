#!/usr/bin/env bash
set -e
# make sure pip deps are installed (Vercel will handle install in build, but this is safe)
python -m pip install -r requirements.txt
# run migrations only if you use a remote DB; skip for sqlite in /tmp
python manage.py collectstatic --noinput
