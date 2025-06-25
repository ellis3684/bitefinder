import os
from pathlib import Path


def read_secret(secret_name):
    """
    Read secret values from Docker secrets or fall back to
    environment variables for local non-Docker runs.
    """
    file_env = secret_name + "_FILE"
    if file_env in os.environ and os.path.exists(os.environ[file_env]):
        with open(os.environ[file_env]) as f:
            return f.read().strip()
    return os.environ.get(secret_name, "")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------
# API Keys & Secrets
# ------------------------------------------------------------------------
FATSECRET_CLIENT_ID = read_secret("FATSECRET_CLIENT_ID")
FATSECRET_CLIENT_SECRET = read_secret("FATSECRET_CLIENT_SECRET")
FOURSQUARE_API_KEY = read_secret("FOURSQUARE_API_KEY")
GOOGLE_PLACES_API_KEY = read_secret("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = read_secret("OPENAI_API_KEY")
SECRET_KEY = read_secret("DJANGO_SECRET_KEY")

# ------------------------------------------------------------------------
# Core Django settings
# ------------------------------------------------------------------------
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "frontend",  # Docker-compose service name (Nginx container)
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",  # Vite dev server
]

AUTH_USER_MODEL = "users.CustomUser"

# ------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
        },
        "django_errors": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django_errors.log",
        },
        "celery_errors": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "celery_errors.log",
        },
        "celery_beat_errors": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "celery_beat_errors.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django_errors"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "django.template": {
            "handlers": ["console", "django_errors"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console", "django_errors"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "celery_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
        "celery.beat": {
            "handlers": ["console", "celery_beat_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
}

# ------------------------------------------------------------------------
# Installed apps & middleware
# ------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "corsheaders",
    "rest_framework",
    "api",
    "menu_items",
    "restaurants",
    "users",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# ------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": read_secret("POSTGRES_PASSWORD"),
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}

# ------------------------------------------------------------------------
# REST Framework
# ------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ------------------------------------------------------------------------
# Celery
# ------------------------------------------------------------------------
CELERY_BROKER_URL = "redis://redis:6379/"
CELERY_RESULT_BACKEND = "redis://redis:6379/"

# ------------------------------------------------------------------------
# Caching (Redis)
# ------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}

# ------------------------------------------------------------------------
# Internationalisation
# ------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------
# Static files
# ------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # /app/staticfiles inside container

# ------------------------------------------------------------------------
# Misc
# ------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
