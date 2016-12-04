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
    }
}

DEBUG = True

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = True
EMAIL['EMAIL_HOST'] = ''
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = ''
EMAIL['EMAIL_HOST_USER'] = ''
EMAIL['DEFAULT_FROM_EMAIL'] = ''
EMAIL['SERVER_EMAIL'] = ''

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = ''
STORAGE['AWS_SECRET_ACCESS_KEY'] = ''
STORAGE['AWS_STORAGE_BUCKET_NAME'] = 'aovdev'
STORAGE['IMAGES_ORIGINAL_BUCKET'] = 'aovdev-original'
STORAGE['REMOTE_IMAGE_STORAGE'] = True
EOF
elif [ "$1" == "staging" ]; then
    cat > backend/settings/project_config.py <<'EOF'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gdb',
        'USER': 'djangostaging',
        'PASSWORD': 'golden',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

DEBUG = True

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = True
EMAIL['EMAIL_HOST'] = ''
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = ''
EMAIL['EMAIL_HOST_USER'] = ''
EMAIL['DEFAULT_FROM_EMAIL'] = ''
EMAIL['SERVER_EMAIL'] = ''

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = ''
STORAGE['AWS_SECRET_ACCESS_KEY'] = ''
STORAGE['AWS_STORAGE_BUCKET_NAME'] = 'aovstaging'
STORAGE['IMAGES_ORIGINAL_BUCKET'] = 'aovstaging-original'
STORAGE['REMOTE_IMAGE_STORAGE'] = True
EOF
elif [ "$1" == "production" ]; then
    cat > backend/settings/project_config.py <<'EOF'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    }
}

DEBUG = False

EMAIL = dict()

EMAIL['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL['EMAIL_USE_TLS'] = True
EMAIL['EMAIL_HOST'] = ''
EMAIL['EMAIL_PORT'] = 587
EMAIL['EMAIL_HOST_PASSWORD'] = ''
EMAIL['EMAIL_HOST_USER'] = ''
EMAIL['DEFAULT_FROM_EMAIL'] = ''
EMAIL['SERVER_EMAIL'] = ''

SOCIAL_AUTH_FACEBOOK_SECRET = ''

STORAGE = dict()

STORAGE['AWS_ACCESS_KEY_ID'] = ''
STORAGE['AWS_SECRET_ACCESS_KEY'] = ''
STORAGE['AWS_STORAGE_BUCKET_NAME'] = 'aovprod'
STORAGE['IMAGES_ORIGINAL_BUCKET'] = 'aovprod-original'
STORAGE['REMOTE_IMAGE_STORAGE'] = True
EOF
else
    echo "No environment specified [dev|staging|production]"
fi