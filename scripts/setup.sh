#!/bin/bash
echo "Setting up '$1'"

if [ "$1" == "dev" ]; then
    cat > backend/settings/project_config.py <<'EOF'
import os

APNS_CERTIFICATE = 'aov_dev.pem'

# TODO change these when ready to enable celery
BROKER_URL = 'redis://{}:{}/2'.format(os.environ.get('REDIS_HOST', '0.0.0.0'), os.environ.get('REDIS_PORT', 6379))
CELERY_RESULT_BACKEND = 'redis://{}:{}/3'.format(os.environ.get('REDIS_HOST', '0.0.0.0'), os.environ.get('REDIS_PORT', 6379))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'aov',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 3600,
    }
}

DEBUG = True

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = False
EMAIL['EMAIL_HOST'] = 'smtp-relay.sendinblue.com'
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = ''
EMAIL['EMAIL_HOST_USER'] = ''
EMAIL['DEFAULT_FROM_EMAIL'] = 'info@artofvisuals.com'
EMAIL['SERVER_EMAIL'] = 'ronquillo.m@gmail.com'

CACHES = {
    "default": {
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": '127.0.0.1:6379:3'
    }
}

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": os.environ.get('FCM_SERVER_KEY'),
    "ONE_DEVICE_PER_USER": True
}

# Simpler hasher for DEV/TESTING only
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

PROFILE_USER = ""
PROFILE_PASSWORD = ""

REDIS_DB = dict()

REDIS_DB['PASSWORD_CODES'] = 1
REDIS_HOST = 'localhost'
REDIS_PASSWORD = None
REDIS_PORT = 6379

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = ''
STORAGE['AWS_SECRET_ACCESS_KEY'] = ''
STORAGE['AWS_STORAGE_BUCKET_NAME'] = ''
STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'] = ''
STORAGE['REMOTE_IMAGE_STORAGE'] = True
STORAGE['REMOTE_AUDIO_STORAGE'] = True
STORAGE['AUDIO_BUCKET_NAME'] = ''

TEMPLATE_OPTIONS = dict()

TEMPLATE_OPTIONS['LOADERS'] = None
EOF
elif [ "$1" == "production" ]; then
    cat > backend/settings/project_config.py <<'EOF'
import os

APNS_CERTIFICATE = os.environ.get('APNS_CERT')

# TODO change these when ready to enable celery
BROKER_URL = 'redis://:{}:{}/2'.format(os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))
CELERY_RESULT_BACKEND = 'redis://:{}:{}/3'.format(os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 3600,
    }
}

DEBUG = bool(os.environ.get('DEBUG', False))

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = False
EMAIL['EMAIL_HOST'] = os.environ['EMAIL_HOST']
EMAIL['EMAIL_PORT'] = os.environ.get('EMAIL_PORT', 587)
EMAIL['EMAIL_HOST_PASSWORD'] = os.environ['EMAIL_HOST_PASSWORD']
EMAIL['EMAIL_HOST_USER'] = os.environ['EMAIL_HOST_USER']
EMAIL['DEFAULT_FROM_EMAIL'] = os.environ['DEFAULT_FROM_EMAIL']
EMAIL['SERVER_EMAIL'] = os.environ['EMAIL_HOST_USER']

CACHES = {
    "default": {
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": 'redis://aovstagingb.oi33ht.ng.0001.usw2.cache.amazonaws.com:6379/3'
    }
}

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": os.environ.get('FCM_SERVER_KEY'),
    "ONE_DEVICE_PER_USER": True
}

PROFILE_USER = ""
PROFILE_PASSWORD = ""

REDIS_DB = dict()

REDIS_DB['PASSWORD_CODES'] = 1
REDIS_DB['AUTHENTICATION_CODES'] = 2
REDIS_DB['CACHE'] = 3
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
STORAGE['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
STORAGE['AWS_STORAGE_BUCKET_NAME'] = os.environ['AWS_STORAGE_BUCKET_NAME']
STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'] = os.environ['IMAGES_ORIGINAL_BUCKET_NAME']
STORAGE['REMOTE_IMAGE_STORAGE'] = os.environ.get('REMOTE_IMAGE_STORAGE', True)
STORAGE['REMOTE_AUDIO_STORAGE'] = os.environ.get('REMOTE_AUDIO_STORAGE', True)
STORAGE['AUDIO_BUCKET_NAME'] = os.environ['AUDIO_BUCKET_NAME']

TEMPLATE_OPTIONS = dict()

TEMPLATE_OPTIONS['LOADERS'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
EOF
else
    echo "No environment specified [dev|production]"
fi