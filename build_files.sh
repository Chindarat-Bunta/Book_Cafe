#!/bin/bash
set -e

echo "==> Preparing staticfiles directory..."
mkdir -p staticfiles

echo "==> Installing requirements..."
python3 -m pip install -r requirements.txt

echo "==> Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "==> Build complete!"
ls -la staticfiles
