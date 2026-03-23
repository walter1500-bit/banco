#!/usr/bin/env bash

pip install -r requeriments.txt
python manage.py collectstatic --noinput
python manage.py migrate
