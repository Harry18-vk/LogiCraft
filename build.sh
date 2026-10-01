#!/usr/bin/env bash
# build.sh — Render build script for LogiCraft Django app
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
