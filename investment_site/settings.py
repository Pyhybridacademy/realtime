import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kpd2@cuv#q5u9qub9ey5w-v(x4_-xk)w3oi9=evce$(=5r)g6m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# For production
ALLOWED_HOSTS = ['realtime-awxx.onrender.com', 'localhost', '127.0.0.1']

# Or if you want to allow all hosts (not recommended for production)
# ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

 # Third-party apps
    'tailwind',
    'crispy_forms',
    'django_countries',
    
    # Project apps
    'accounts',
    'dashboard',
    'wallet',
    'transactions',
    'admin_panel',
    'notifications',
    'user_actions',
]

# Tailwind configuration
TAILWIND_APP_NAME = 'theme'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_panel.middleware.MaintenanceModeMiddleware',
    'investment_site.middleware.PendingActionMiddleware',
]

ROOT_URLCONF = 'investment_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications',
                'admin_panel.context_processors.system_settings',
                'admin_panel.context_processors.admin_stats',
                'wallet.context_processors.exchange_rates',
            ],
        },
    },
]

WSGI_APPLICATION = 'investment_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom user model
AUTH_USER_MODEL = 'accounts.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Make sure you have this for serving static files in production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Login URL
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# Add these settings to your settings.py
LOGOUT_URL = '/accounts/logout/'
LOGOUT_REDIRECT_URL = '/accounts/login/'  # Where to redirect after logout


STATIC_ROOT = BASE_DIR / 'staticfiles'  # Or another appropriate directory
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Where you'll put your static files
]

# Email settings - these will be overridden by SystemSettings if available
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'Investment Platform <noreply@yourdomain.com>'

# For development, you can use the console backend
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Site URL for links in emails
SITE_URL = 'https://realtime-awxx.onrender.com'  # Change this in production

# Add this to your settings.py file
CSRF_TRUSTED_ORIGINS = ['https://realtime-awxx.onrender.com']
