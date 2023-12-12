import os
import dj_database_url

from environs import Env
import urllib.parse

env = Env()
env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


SECRET_KEY = env('SECRET_KEY')
YANDEX_API_KEY = env('YANDEX_API_KEY')
DEBUG = env.bool('DEBUG', False)

# ALLOWED_HOSTS = ['82.148.30.157', '0.0.0.0', '127.0.0.1', 'localhost', 'sgkespace.ru', 'http://sgkespace.ru', 'www.sgkespace.ru', 'https://sgkespace.ru']
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', ['127.0.0.1', 'localhost'])

INSTALLED_APPS = [
    'foodcartapp.apps.FoodcartappConfig',
    'restaurateur.apps.RestaurateurConfig',
    'location.apps.LocationConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddlewareExcluding404',
]

ROOT_URLCONF = 'star_burger.urls'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
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

WSGI_APPLICATION = 'star_burger.wsgi.application'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


POSTGRES_URL_PARSED = env('POSTGRES_URL').split(':')

POSTGRES_URL_PARSED[1] = '//' + urllib.parse.quote(POSTGRES_URL_PARSED[1][2:])

index = 0
for iters, char in enumerate(POSTGRES_URL_PARSED[2][::-1]):
    if char == '@':
        index = iters
        break
password = urllib.parse.quote(POSTGRES_URL_PARSED[2][:-index-1])
host = POSTGRES_URL_PARSED[2][-index:]
POSTGRES_URL_PARSED[2] = '@'.join([password, host])

POSTGRES_URL_PARSED = ':'.join(POSTGRES_URL_PARSED)

DATABASES = {
    'default': dj_database_url.parse(
        POSTGRES_URL_PARSED,
    )
}

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

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

INTERNAL_IPS = [
    '127.0.0.1'
]


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
    os.path.join(BASE_DIR, "bundles"),
    os.path.join(BASE_DIR, "templates"),
    os.path.join(BASE_DIR, "restaurateur/templates"),
    os.path.join(BASE_DIR, "foodcartapp/static"),
]


ROLLBAR = {
    'access_token': env('ROLLBAR_ACCESS_TOKEN'),
    'environment': 'development' if env.bool('ROLLBAR_ENVIRONMENT_DEVELOPMENT', False) else 'production',
    'code_version': '1.0',
    'root': BASE_DIR,
}
