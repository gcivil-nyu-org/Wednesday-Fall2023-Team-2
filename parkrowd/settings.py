"""Parkrowd App Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from utils.aws_utils import get_linux_ec2_private_ip

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load the .env file
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), verbose=False)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-fwhre62z62nwjg@ft0(-6^pt6@aaa$p+ha0xdsl$qpk5j0sc#n"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("PROD") == "false"

# allowed hosts settings
ALLOWED_HOSTS = [
    "Parkrowd-env.eba-spjjw3yh.us-west-2.elasticbeanstalk.com"
    if os.getenv("PROD") != "false"
    else "127.0.0.1"
]
# ElasticBeanstalk healthcheck sends requests with host header = internal ip
# So we detect if we are in elastic beanstalk,
# and add the instances private ip address
private_ip = get_linux_ec2_private_ip()
if private_ip:
    ALLOWED_HOSTS += [private_ip]


# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "users.apps.UsersConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "parkrowd.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "parkrowd/templates")],
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

WSGI_APPLICATION = "parkrowd.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "PORT": os.getenv("RDS_PORT"),
        "USER": os.getenv("RDS_USERNAME"),
        "HOST": os.getenv("RDS_HOSTNAME"),
        "NAME": os.getenv("RDS_DB_NAME"),
        "PASSWORD": os.getenv("RDS_PASSWORD"),
        "ENGINE": "django.db.backends.postgresql",
    }
}

# Custom User Model for Authorization
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "users.backends.EmailOrUsernameAuthenticationBackend",
]

LOGOUT_REDIRECT_URL = "/login"

# session expiry default setting
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Changes messages to be based on SessionStorage, not CookieStorage
# To fix bug with messages still appearing on screen, after logging out
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

# TODO: not sure why translation and localizing time is needed
# USE_TZ = True
# USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "static"
# Image File Setup
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
