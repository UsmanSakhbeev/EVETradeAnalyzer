#!/bin/sh

python manage.py migrate
gunicorn evetradeanalyzer.wsgi:application --bind 0.0.0.0:8000
