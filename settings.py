# -*- coding: utf-8 -*-
import os
from django.conf.global_settings import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'op_esb_template',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


SECRET_KEY = '3Vfh83mtBd25h3nj3bia3HMp9gQn57l9fZfn3fiZinzbyi3f3'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True

TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'esb',
    'esb.bkcore',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'esb.middlewares.APICommonMiddleware',
)

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'


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
                'django.core.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )


LOG_LEVEL = 'INFO'
LOG_DIR = os.path.join(os.path.dirname(BASE_DIR), 'logs/open_paas')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d \n \t %(message)s \n',    # noqa
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'root': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIR, 'esb.log'),
            'maxBytes': 104857600,
            'backupCount': 5
        },
        'api': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(LOG_DIR, 'esb_api.log'),
            'maxBytes': 104857600,
            'backupCount': 5
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['root'],
            'level': 'ERROR',
            'propagate': True,
        },
        'root': {
            'handlers': ['root'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'api': {
            'handlers': ['api'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'esb.management': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


SITE_URL = '/'
STATIC_URL = SITE_URL + 'static/'
STATIC_VERSION = '0.0.1'


COMPONENT_CONFIG = {
    'component_base_path': os.path.join(BASE_DIR, 'components/generic/apis/'),
    'name_prefix': 'generic.',
}
