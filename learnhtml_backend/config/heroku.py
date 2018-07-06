import os

from configurations import values

from learnhtml_backend.config.common import Common


class Heroku(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn",)

    RQ_QUEUES = {
        'default': {
            'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),  # If you're on Heroku
            'DEFAULT_TIMEOUT': 600,
        },
    }

    CORS_ORIGIN_WHITELIST = (
        values.URLValue('http://localhost:8000', environ_name='CORS_ORIGIN'),
    )
