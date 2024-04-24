from pathlib import Path
import os
import django_heroku,dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.python
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES_URL = 'postgres://hozexrnxqcnxts:c90c72720d1f9cfb3c7bbf19fc6f35380dc4ea308017bf96920e595aa8b2d384@ec2-54-84-182-168.compute-1.amazonaws.com:5432/de22sdi8c6sffu'
DATABASES_URLS = 'postgres://pams_user:xUBo8ZEU0X95oT0Eh7BPFrROy3Pxi38K@dpg-ci6unsh8g3n3vm3g5sdg-a.oregon-postgres.render.com/pams'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-pa=aq6!i*u#!___e03p%vu%+fzi*k9$)p@jr8w0kg&rwndm$0x"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'archives',
    'corsheaders',
    
    
    
]

MIDDLEWARE = [
     'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
     "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ROOT_URLCONF = "projectArchives.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "projectArchives.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


###############LOCAL #####################
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'archives',
#         'USER': 'postgres',
#         'PASSWORD': 'raphael',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }

##################HEROKU#########################
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'd6khn9imgr5rn6',
#         'USER': 'postgres',
#         'PASSWORD': 'RDlJOqOuli0bScgw7v8P',
#         'HOST': 'ec2-3-208-74-199.compute-1.amazonaws.com',
#         'PORT': '6223',
#     }
# }

########### RENDER ##################
# import dj_database_url
# DATABASES = {
#      'default': dj_database_url.parse(DATABASES_URLS)
#          }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

# STATIC_DIRS = [
#     os.path.join(BASE_DIR,'static')
# ]
# STATIC_ROOT = os.path.join(BASE_DIR,'static')
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



from django.contrib.messages import constants as messages


MESSAGE_TAGS = {
    messages.DEBUG: 'alert alert-info',
    messages.INFO: 'alert alert-info',
    messages.SUCCESS: 'alert alert-success',
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-danger',
}

X_FRAME_OPTIONS = 'SAMEORGIN'

CORS_ALLOW_ALL_ORIGINS: True
CORS_ALLOW_CREDENTIALS = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# AUTH_USER_MODEL = 'archives.User'


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
#django_heroku.settings(locals())
APPEND_SLASH=False