web: DJANGO_SETTINGS_MODULE DJANGO_CONFIGURATION=Heroku gunicorn --pythonpath="$PWD" learnhtml_backend.wsgi:application
worker:  DJANGO_CONFIGURATION=Heroku python manage.py rqworker default
