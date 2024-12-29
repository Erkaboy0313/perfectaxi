"""
Django settings for PerfectTaxi project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY','asdfwefef2131a#sefej43;k2ijo2i34i90ri90feoire902390ii912f')

# DEBUG = True
DEBUG = int(os.environ.get('DEBUG',1))

# ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS','127.0.0.1 localhost').split(' ')
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

HOST ='http://127.0.0.1:8000' if DEBUG else 'https://api.perfecttaxi.uz'
    
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'ws.apps.WsConfig',
    'chat',
    'category',
    'creditCard',
    'feedback',
    'notification',
    'order',
    'payment',
    'pricing',
    'rest_framework',
    'rest_framework.authtoken',
    "debug_toolbar",
    'django_celery_results',
    "django_celery_beat",
    'corsheaders',
    'dashboard'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'PerfectTaxi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'PerfectTaxi.wsgi.application'
ASGI_APPLICATION = 'PerfectTaxi.asgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Replace with desired permissions
    ],
    'DATETIME_FORMAT': '%d-%m-%Y %H:%M:%S'
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_HOST1',"127.0.0.1"), 6379)],
        },
    },
}

CELERY_BROKER_URL = f'redis://{os.environ.get("REDIS_HOST1","127.0.0.1")}:6379/0'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


CSRF_COOKIE_SECURE = False
CORS_ALLOW_CREDENTIALS = True

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.environ.get('REDIS_HOST1','127.0.0.1')}:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "PTaxi",
    }
}

DATABASES = {
    # 'default': {
    #     'ENGINE': os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
    #     'NAME': os.environ.get("SQL_DATABASE", "ptaxi"),
    #     'USER': os.environ.get("SQL_USER", "eric"),
    #     'PASSWORD': os.environ.get("SQL_PASSWORD", "nevergiveup3"),
    #     'HOST': os.environ.get("SQL_HOST", "localhost"),
    #     'PORT': os.environ.get("SQL_PORT", "5432"),
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'taxi',
        'USER': 'taxiadmin',
        'PASSWORD': 'taxiadmin',
        'HOST': 'localhost',
        'PORT': '',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "info": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                'filename': BASE_DIR / 'info.log',
            },
            "error": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                'filename': BASE_DIR / 'error.log',
            },
        },
        "loggers": {
            "django": {
                "handlers": ["info"],
                "level":"INFO",
                "propagate": True,
            },
            "": {
                "handlers": ["error"],
                "level":"ERROR",
                "propagate": True,
            },
        },
    }


PAYMENT_VARIANTS = {
    'click' : ('click.ClickProvider', {
        'merchant_id' : os.environ.get("CLICK_MERCHAT_ID","30270"),
        'merchant_service_id' : os.environ.get("CLICK_SERVICE_ID","22771"),
        'merchant_user_id' : os.environ.get("CLICK_USER_ID","36304"),
        'secret_key' : os.environ.get("CLICK_SECRET_KEY","oBVfbPss7Fa")
    })
}


AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'staticfiles/'
STATIC_ROOT  =  os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
INTERNAL_IPS = [
    "127.0.0.1",
]