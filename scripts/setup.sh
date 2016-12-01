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

IMAGES_USE_REMOTE_STORAGE = False

SOCIAL_AUTH_FACEBOOK_SECRET = ''
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

IMAGES_USE_REMOTE_STORAGE = True

SOCIAL_AUTH_FACEBOOK_SECRET = ''
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

IMAGES_USE_REMOTE_STORAGE = True

SOCIAL_AUTH_FACEBOOK_SECRET = ''
EOF
else
    echo "No environment specified [dev|staging|production]"
fi