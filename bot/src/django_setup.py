import os
import sys

import django
from django.conf import settings
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
admin_panel_path = os.path.join(BASE_DIR, 'admin_panel')

load_dotenv()


def setup_django():
    """Настройка Django."""

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': os.getenv('NAME'),
                    'USER': os.getenv('USER'),
                    'PASSWORD': os.getenv('PASSWORD'),
                    'HOST': os.getenv('HOST'),
                    'PORT': os.getenv('PORT'),
                    'OPTIONS': {
                        'connect_timeout': 5,
                    },
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'admin_panel.app',
            ],
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )

    django.setup()
