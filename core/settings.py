"""
Django settings for projeto project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import mimetypes
mimetypes.add_type("text/css", ".css", True)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECURE_SSL_REDIRECT = False


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r)%(=%h%#yp&fyl^xkh51v6(k3scqlyn)w=_x)q-(!i_fucvzw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'categorias',
    'crispy_forms', 
    'payments',
    'pedidos',
    'rest_framework'
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projeto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'projeto.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
#STATIC_URL = '/home/emagrecimentodefinitivo/apps_wsgi/projeto/static/'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'core/static',
    BASE_DIR / 'payments/static',
    BASE_DIR / 'pedidos/static',

]
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
#configurações para deploy
N_DEBUG = DEBUG
if N_DEBUG:
    SECURE_SSL_REDIRECT = True
    ALLOWED_HOSTS = ['www.emagrecimentodefinitivo.app.br', 'emagrecimentodefinitivo.app.br']
    DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql',
                'HOST': 'mysql21-farm10.kinghost.net',
                'NAME': 'emagrecimentod',
                'USER': 'emagrecimentod',
                'PASSWORD': 'senhad1',
            }
    }
    STATIC_URL = '/static/'
    STATIC_ROOT = '/home/emagrecimentodefinitivo/www/static'

    MEDIA_URL = 'media/'
    MEDIA_ROOT = '/home/emagrecimentodefinitivo/www/media'
    

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from django.contrib.messages import constants

MESSAGE_TAGS = {
    constants.ERROR: "alert-danger",
    constants.WARNING: "alert-warning",
    constants.SUCCESS: "alert-success"
}

# Mercado Pago
MERCADO_PAGO_PUBLIC_KEY="APP_USR-e4e83140-897a-4c35-9e07-ea8dbc59a007"
MERCADO_PAGO_ACCESS_TOKEN="APP_USR-8889274133618814-042813-84e6c7e1760a577bc6a3768d090240ec-1038289871"

X_FRAME_OPTIONS = 'SAMEORIGIN'
INSTALLED_APPS += ('django_summernote', )

EMAIL_HOST = 'smtp.kinghost.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'nao-responda@emagrecimentodefinitivo.app.br'
EMAIL_HOST_PASSWORD = 'Emagrecimento*22'
