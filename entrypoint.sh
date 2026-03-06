#!/bin/sh
set -e

mkdir -p /app/data

python manage.py migrate --noinput
python manage.py seed_data

python manage.py runserver 0.0.0.0:8000
