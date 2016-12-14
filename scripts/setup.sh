#!/bin/bash
echo "Setting up '$1'"

if [ "$1" == "dev" ]; then
    cat > backend/settings/project_config.py <<'EOF'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aov',
        'USER': 'djangodev',
        'PASSWORD': 'golden',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 3600,
    }
}

DEBUG = True

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = True
EMAIL['EMAIL_HOST'] = 'smtp-relay.sendinblue.com'
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = 'TzNv13Ohx0tSUwnL'
EMAIL['EMAIL_HOST_USER'] = 'ronquillo.m@gmail.com'
EMAIL['DEFAULT_FROM_EMAIL'] = 'info@artofvisuals.com'
EMAIL['SERVER_EMAIL'] = 'ronquillo.m@gmail.com'

# Simpler hasher for DEV/TESTING only
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

REDIS_DB = dict()

REDIS_DB['PASSWORD_CODES'] = 1
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = ''
STORAGE['AWS_SECRET_ACCESS_KEY'] = ''
STORAGE['AWS_STORAGE_BUCKET_NAME'] = 'aovdev'
STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'] = 'aovdev-original'
STORAGE['REMOTE_IMAGE_STORAGE'] = True

TEMPLATE_OPTIONS = dict()

TEMPLATE_OPTIONS['LOADERS'] = None
EOF
elif [ "$1" == "staging" ]; then
    cat > backend/settings/project_config.py <<'EOF'
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 3600,
    }
}

DEBUG = True

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = True
EMAIL['EMAIL_HOST'] = 'smtp-relay.sendinblue.com'
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = 'TzNv13Ohx0tSUwnL'
EMAIL['EMAIL_HOST_USER'] = 'ronquillo.m@gmail.com'
EMAIL['DEFAULT_FROM_EMAIL'] = 'info@artofvisuals.com'
EMAIL['SERVER_EMAIL'] = 'ronquillo.m@gmail.com'

REDIS_DB = dict()

REDIS_DB['PASSWORD_CODES'] = 1
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
STORAGE['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
STORAGE['AWS_STORAGE_BUCKET_NAME'] = 'aovstaging'
STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'] = 'aovstaging-original'
STORAGE['REMOTE_IMAGE_STORAGE'] = True

TEMPLATE_OPTIONS = dict()

TEMPLATE_OPTIONS['LOADERS'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
EOF
elif [ "$1" == "production" ]; then
    cat > backend/settings/project_config.py <<'EOF'
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 3600,
    }
}

DEBUG = False

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = True
EMAIL['EMAIL_HOST'] = 'smtp-relay.sendinblue.com'
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = 'TzNv13Ohx0tSUwnL'
EMAIL['EMAIL_HOST_USER'] = 'ronquillo.m@gmail.com'
EMAIL['DEFAULT_FROM_EMAIL'] = 'info@artofvisuals.com'
EMAIL['SERVER_EMAIL'] = 'ronquillo.m@gmail.com'

REDIS_DB = dict()

REDIS_DB['PASSWORD_CODES'] = 1
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
STORAGE['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
STORAGE['AWS_STORAGE_BUCKET_NAME'] = 'aovprod'
STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'] = 'aovprod-original'
STORAGE['REMOTE_IMAGE_STORAGE'] = True

TEMPLATE_OPTIONS = dict()

TEMPLATE_OPTIONS['LOADERS'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
EOF
else
    echo "No environment specified [dev|staging|production]"
fi