web: DJANGO_CONFIGURATION=Heroku gunicorn --pythonpath="$PWD" learnhtml_backend.wsgi:application
worker: python DJANGO_CONFIGURATION=Heroku manage.py rqworker default
