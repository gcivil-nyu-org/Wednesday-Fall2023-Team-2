"""Parkrowd App Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy

from utils.aws_utils import get_linux_ec2_private_ip

# region: prep
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# load the .env file
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), verbose=False)
# endregion: prep


# region: django default (likely remain unchanged)
# load secret key from OS env to keep it secret
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# GOOGLE MAPS API Key :
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# use OS env to control this
DEBUG = os.getenv("PROD") == "false"

# * Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
# TODO: not sure why translation and localizing time is needed
# USE_TZ = True
# USE_I18N = True

# * Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# * Session expiry default setting
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# wsgi application
WSGI_APPLICATION = "parkrowd.wsgi.application"

# * Template engine and template directories
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


# *Password validation
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
# endregion: django default (likely remain unchanged)

# region: production related (likely to be changed)
ROOT_URLCONF = "parkrowd.urls"

# * Allowed hosts settings
ALLOWED_HOSTS = [
    "127.0.0.1"
    if os.getenv("PROD") == "false"
    else "parkrowd-env.eba-spjjw3yh.us-west-2.elasticbeanstalk.com"
]
# ElasticBeanstalk healthcheck sends requests with host header = internal ip
# So we detect if we are in elastic beanstalk,
# and add the instances private ip address
private_ip = get_linux_ec2_private_ip()
if private_ip:
    ALLOWED_HOSTS += [private_ip]

# * Custom User Model for Authorization
AUTH_USER_MODEL = "users.User"

LOGIN_URL = reverse_lazy("users:login")
LOGOUT_REDIRECT_URL = reverse_lazy("users:login")
AUTHENTICATION_BACKENDS = ["users.backends.EmailOrUsernameAuthenticationBackend"]

# Changes messages to be based on SessionStorage, not CookieStorage
# To fix bug with messages still appearing on screen, after logging out
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# * Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = "static"
# Image File Setup
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# * Email functionality
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587 if EMAIL_USE_TLS else 465
EMAIL_HOST_USER = os.getenv("GOOGLE_SMTP_USERNAME")
DEFAULT_FROM_EMAIL = os.getenv("GOOGLE_SMTP_USERNAME")
EMAIL_HOST_PASSWORD = os.getenv("GOOGLE_SMTP_PASSWORD")
EMAIL_FILE_PATH = (
    BASE_DIR / os.getenv("DEV_EMAIL_STORE_RELATIVE_PATH")
    if os.getenv("PROD") == "false"
    else None
)
EMAIL_BACKEND = (
    "django.core.mail.backends.filebased.EmailBackend"
    if os.getenv("PROD") == "false"
    else "django.core.mail.backends.smtp.EmailBackend"
)

# * Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "map.apps.MapConfig",
    "users.apps.UsersConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    'django_extensions',
]

# * Middleware definition
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# * Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# DATABASES = {
#     "default": {
#         "PORT": os.getenv("RDS_PORT"),
#         "USER": os.getenv("RDS_USERNAME"),
#         "HOST": os.getenv("RDS_HOSTNAME"),
#         "NAME": os.getenv("RDS_DB_NAME"),
#         "PASSWORD": os.getenv("RDS_PASSWORD"),
#         "ENGINE": "django.db.backends.postgresql",
#     }
# }
# endregion: production related (likely to be changed)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
